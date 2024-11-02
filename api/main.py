from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ariadne import gql, make_executable_schema, ObjectType, MutationType, QueryType
from ariadne.asgi import GraphQL
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from zuul_core_ledger import Account, ZuulCoreLedger

# Initialize FastAPI app
app = FastAPI()

# CORS setup to allow all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify the actual origin, e.g., ["http://localhost:8080"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB client and database
client = AsyncIOMotorClient("mongodb://mongodb:27017")
db = client.zuul_core_banking

# Initialize core banking ledger
ledger = ZuulCoreLedger()

# Define GraphQL schema
type_defs = gql("""
    type User {
        account_id: String
        customer_name: String
        funds: Float
        loans: Float
        interest_rate: Float
        action_history: [String]
    }

    type Mutation {
        createUser(account_id: String!, customer_name: String!, funds: Float!, interest_rate: Float!): User
        updateFunds(account_id: String!, amount: Float!): String
        addActionHistory(account_id: String!, action: String!): String
        deposit(account_id: String!, amount: Float!): String
        withdraw(account_id: String!, amount: Float!): String
        transfer(from_account_id: String!, to_account_id: String!, amount: Float!): String
    }

    type Query {
        user(account_id: String!): User
    }
""")

# Define resolvers for the schema
query = QueryType()
mutation = MutationType()

# User Query Resolver
@query.field("user")
async def resolve_user(_, info, account_id):
    user = await db.users.find_one({"account_id": account_id})
    if user:
        return {
            "account_id": user["account_id"],
            "customer_name": user["customer_name"],
            "funds": user["funds"],
            "loans": user["loans"],
            "interest_rate": user["interest_rate"],
            "action_history": user["action_history"]
        }
    return None

# Mutation resolvers
@mutation.field("createUser")
async def resolve_create_user(_, info, account_id, customer_name, funds, interest_rate):
    user_data = {
        "account_id": account_id,
        "customer_name": customer_name,
        "funds": funds,
        "interest_rate": interest_rate,
        "loans": 0.0,
        "action_history": []
    }
    await db.users.insert_one(user_data)
    return user_data

@mutation.field("updateFunds")
async def resolve_update_funds(_, info, account_id, amount):
    user = await db.users.find_one({"account_id": account_id})
    if user:
        await db.users.update_one(
            {"account_id": account_id},
            {"$inc": {"funds": amount}}
        )
        return "Funds updated successfully."
    return "User not found."

@mutation.field("addActionHistory")
async def resolve_add_action_history(_, info, account_id, action):
    timestamped_action = f"{datetime.now().isoformat()} - {action}"
    await db.users.update_one(
        {"account_id": account_id},
        {"$push": {"action_history": timestamped_action}}
    )
    return "Action added to history."

@mutation.field("deposit")
async def resolve_deposit(_, info, account_id, amount):
    result = ledger.deposit(account_id, amount)
    await resolve_add_action_history(_, info, account_id, f"Deposited {amount}")
    return result

@mutation.field("withdraw")
async def resolve_withdraw(_, info, account_id, amount):
    result = ledger.withdraw(account_id, amount)
    await resolve_add_action_history(_, info, account_id, f"Withdrew {amount}")
    return result

@mutation.field("transfer")
async def resolve_transfer(_, info, from_account_id, to_account_id, amount):
    # Check if both accounts exist
    from_account = await db.users.find_one({"account_id": from_account_id})
    to_account = await db.users.find_one({"account_id": to_account_id})

    if not from_account:
        return "Sender account not found."
    if not to_account:
        return "Recipient account not found."
    if from_account["funds"] < amount:
        return "Insufficient funds in sender's account."

    # Deduct amount from sender's account
    await db.users.update_one(
        {"account_id": from_account_id},
        {"$inc": {"funds": -amount}}
    )

    # Add amount to recipient's account
    await db.users.update_one(
        {"account_id": to_account_id},
        {"$inc": {"funds": amount}}
    )

    # Add action history for both accounts
    await resolve_add_action_history(info, from_account_id, f"Transferred {amount} to {to_account_id}")
    await resolve_add_action_history(info, to_account_id, f"Received {amount} from {from_account_id}")

    return "Transfer completed successfully."

# Create the executable schema and add it to the FastAPI app
schema = make_executable_schema(type_defs, query, mutation)
app.add_route("/graphql", GraphQL(schema, debug=True))

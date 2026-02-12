"""
Smart Recipe Engine - FastAPI Backend with MongoDB
Complete backend in a single main.py file
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from contextlib import asynccontextmanager

# ==================== Configuration ====================
# MongoDB connection - defaults to localhost if not set
# MONGODB_URL = os.getenv("MONGODB_URL") or os.getenv("MONGODB_URI") or "mongodb://localhost:27017"
# DB_NAME="recipes"
# RECIPES_COLLECTION = "recipe_ai"
MONGODB_URL="mongodb+srv://Meghana:Meghana123@cluster1.4cq0cxs.mongodb.net/?appName=Cluster1"
DB_NAME="recipes"
RECIPES_COLLECTION = "recipe_ai"
# ==================== MongoDB Client ====================
mongodb_client: Optional[AsyncIOMotorClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MongoDB connection lifecycle"""
    global mongodb_client
    # Startup: Connect to MongoDB
    mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    try:
        # Test connection
        await mongodb_client.admin.command('ping')
        print(f"✓ Connected to MongoDB at {MONGODB_URL}")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
    
    yield
    
    # Shutdown: Close MongoDB connection
    if mongodb_client:
        mongodb_client.close()
        print("✓ MongoDB connection closed")

# ==================== FastAPI App ====================
app = FastAPI(
    title="Smart Recipe Engine API",
    description="AI-powered recipe management with intelligent substitutions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Helper Functions ====================
def get_database():
    """Get MongoDB database instance"""
    return mongodb_client[DB_NAME]

def get_recipes_collection():
    """Get recipes collection"""
    return get_database()[RECIPES_COLLECTION]

def recipe_helper(recipe) -> dict:
    """Convert MongoDB document to dict with string _id"""
    return {
        "_id": str(recipe["_id"]),
        "title": recipe.get("title", ""),
        "ingredients": recipe.get("ingredients", []),
        "instructions": recipe.get("instructions", ""),
        "diet_tags": recipe.get("diet_tags", []),
        "calories": recipe.get("calories"),
        "cuisine": recipe.get("cuisine"),
    }

# ==================== Pydantic Models ====================
class Ingredient(BaseModel):
    name: str
    quantity: str = ""

class RecipeCreate(BaseModel):
    title: str
    ingredients: List[Ingredient]
    instructions: str = ""
    diet_tags: List[str] = []
    calories: Optional[int] = None
    cuisine: Optional[str] = None

class RecipeResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    ingredients: List[Ingredient]
    instructions: str
    diet_tags: List[str]
    calories: Optional[int]
    cuisine: Optional[str]

    class Config:
        populate_by_name = True

class RecipeSearchRequest(BaseModel):
    ingredients: List[str] = []
    diet_tags: List[str] = []
    max_calories: Optional[int] = None

class SubstituteRequest(BaseModel):
    ingredient: str
    goal: str = "healthier"  # healthier, vegan, low_calorie, any

class SubstituteItem(BaseModel):
    name: str
    reason: str
    health_tags: List[str] = []

class SubstituteResponse(BaseModel):
    original: str
    goal: str
    substitutes: List[SubstituteItem]

# ==================== Substitution Knowledge Base ====================
INGREDIENT_SUBSTITUTIONS = {
    "sugar": {
        "healthier": [
            {"name": "Stevia", "reason": "Zero calories, natural sweetener", "health_tags": ["zero_calorie", "natural", "diabetic_friendly"]},
            {"name": "Honey", "reason": "Natural sweetener with antioxidants", "health_tags": ["natural", "antioxidants"]},
            {"name": "Jaggery", "reason": "Unrefined sugar with minerals", "health_tags": ["natural", "mineral_rich"]},
            {"name": "Maple Syrup", "reason": "Natural sweetener with minerals", "health_tags": ["natural", "antioxidants"]},
        ],
        "vegan": [
            {"name": "Maple Syrup", "reason": "100% plant-based sweetener", "health_tags": ["vegan", "natural"]},
            {"name": "Agave Nectar", "reason": "Plant-based, low glycemic index", "health_tags": ["vegan", "low_gi"]},
            {"name": "Coconut Sugar", "reason": "Vegan, sustainable sweetener", "health_tags": ["vegan", "sustainable"]},
        ],
        "low_calorie": [
            {"name": "Stevia", "reason": "Zero calories, very sweet", "health_tags": ["zero_calorie", "natural"]},
            {"name": "Erythritol", "reason": "Near zero calories, sugar alcohol", "health_tags": ["low_calorie", "sugar_alcohol"]},
        ],
    },
    "milk": {
        "healthier": [
            {"name": "Almond Milk", "reason": "Low calorie, lactose-free", "health_tags": ["low_calorie", "lactose_free", "plant_based"]},
            {"name": "Oat Milk", "reason": "High fiber, heart-healthy", "health_tags": ["high_fiber", "heart_healthy", "plant_based"]},
            {"name": "Skim Milk", "reason": "Low fat, high protein", "health_tags": ["low_fat", "high_protein"]},
        ],
        "vegan": [
            {"name": "Soy Milk", "reason": "High protein, plant-based", "health_tags": ["vegan", "high_protein", "plant_based"]},
            {"name": "Almond Milk", "reason": "Dairy-free, nut-based", "health_tags": ["vegan", "dairy_free", "plant_based"]},
            {"name": "Coconut Milk", "reason": "Creamy, dairy-free alternative", "health_tags": ["vegan", "dairy_free", "creamy"]},
            {"name": "Oat Milk", "reason": "Sustainable, plant-based", "health_tags": ["vegan", "sustainable", "plant_based"]},
        ],
        "low_calorie": [
            {"name": "Almond Milk (unsweetened)", "reason": "30-40 calories per cup", "health_tags": ["low_calorie", "unsweetened"]},
            {"name": "Cashew Milk", "reason": "Low calorie, creamy texture", "health_tags": ["low_calorie", "plant_based"]},
        ],
    },
    "butter": {
        "healthier": [
            {"name": "Olive Oil", "reason": "Heart-healthy fats, antioxidants", "health_tags": ["heart_healthy", "antioxidants", "healthy_fats"]},
            {"name": "Avocado Oil", "reason": "High in monounsaturated fats", "health_tags": ["healthy_fats", "high_smoke_point"]},
            {"name": "Greek Yogurt", "reason": "Lower fat, high protein (for baking)", "health_tags": ["high_protein", "low_fat"]},
        ],
        "vegan": [
            {"name": "Coconut Oil", "reason": "Plant-based, versatile", "health_tags": ["vegan", "plant_based", "versatile"]},
            {"name": "Vegan Butter", "reason": "Direct butter replacement", "health_tags": ["vegan", "plant_based"]},
            {"name": "Olive Oil", "reason": "Healthy, plant-based fat", "health_tags": ["vegan", "heart_healthy"]},
        ],
        "low_calorie": [
            {"name": "Applesauce", "reason": "Low calorie, for baking", "health_tags": ["low_calorie", "fruit_based"]},
            {"name": "Greek Yogurt", "reason": "Lower calories than butter", "health_tags": ["low_calorie", "high_protein"]},
        ],
    },
    "eggs": {
        "healthier": [
            {"name": "Egg Whites", "reason": "Pure protein, no cholesterol", "health_tags": ["high_protein", "low_cholesterol", "low_calorie"]},
            {"name": "Whole Eggs (organic)", "reason": "Complete protein, vitamins", "health_tags": ["high_protein", "vitamin_rich"]},
        ],
        "vegan": [
            {"name": "Flax Eggs", "reason": "1 tbsp flax + 3 tbsp water per egg", "health_tags": ["vegan", "omega3", "plant_based"]},
            {"name": "Chia Seeds", "reason": "High fiber, binding properties", "health_tags": ["vegan", "high_fiber", "plant_based"]},
            {"name": "Applesauce", "reason": "1/4 cup per egg for baking", "health_tags": ["vegan", "fruit_based"]},
            {"name": "Silken Tofu", "reason": "1/4 cup per egg, protein-rich", "health_tags": ["vegan", "high_protein"]},
        ],
        "low_calorie": [
            {"name": "Egg Whites", "reason": "17 calories vs 70 for whole egg", "health_tags": ["low_calorie", "high_protein"]},
        ],
    },
    "cream": {
        "healthier": [
            {"name": "Greek Yogurt", "reason": "High protein, lower fat", "health_tags": ["high_protein", "low_fat", "probiotic"]},
            {"name": "Coconut Cream", "reason": "Dairy-free, rich texture", "health_tags": ["dairy_free", "plant_based"]},
        ],
        "vegan": [
            {"name": "Coconut Cream", "reason": "Thick, creamy, plant-based", "health_tags": ["vegan", "dairy_free", "rich"]},
            {"name": "Cashew Cream", "reason": "Blend soaked cashews with water", "health_tags": ["vegan", "plant_based", "smooth"]},
            {"name": "Oat Cream", "reason": "Commercial dairy-free cream", "health_tags": ["vegan", "sustainable"]},
        ],
        "low_calorie": [
            {"name": "Evaporated Skim Milk", "reason": "Much lower fat content", "health_tags": ["low_calorie", "low_fat"]},
            {"name": "Greek Yogurt", "reason": "Creamy with less calories", "health_tags": ["low_calorie", "high_protein"]},
        ],
    },
    "flour": {
        "healthier": [
            {"name": "Whole Wheat Flour", "reason": "Higher fiber and nutrients", "health_tags": ["high_fiber", "whole_grain", "nutrient_rich"]},
            {"name": "Almond Flour", "reason": "Low carb, high protein", "health_tags": ["low_carb", "high_protein", "gluten_free"]},
            {"name": "Oat Flour", "reason": "High fiber, heart-healthy", "health_tags": ["high_fiber", "heart_healthy", "gluten_free"]},
        ],
        "vegan": [
            {"name": "Any flour is vegan", "reason": "All flours are plant-based", "health_tags": ["vegan", "plant_based"]},
        ],
        "low_calorie": [
            {"name": "Coconut Flour", "reason": "High fiber, absorbs liquid", "health_tags": ["low_calorie", "high_fiber", "gluten_free"]},
            {"name": "Almond Flour", "reason": "Nutrient-dense, lower carb", "health_tags": ["low_carb", "high_protein"]},
        ],
    },
    "rice": {
        "healthier": [
            {"name": "Brown Rice", "reason": "Whole grain, more fiber", "health_tags": ["whole_grain", "high_fiber", "nutrient_rich"]},
            {"name": "Quinoa", "reason": "Complete protein, high fiber", "health_tags": ["high_protein", "high_fiber", "gluten_free"]},
            {"name": "Cauliflower Rice", "reason": "Very low carb, veggie-based", "health_tags": ["low_carb", "low_calorie", "vegetable"]},
        ],
        "vegan": [
            {"name": "Rice is already vegan", "reason": "All rice varieties are plant-based", "health_tags": ["vegan", "plant_based"]},
        ],
        "low_calorie": [
            {"name": "Cauliflower Rice", "reason": "25 calories vs 200 for white rice", "health_tags": ["low_calorie", "low_carb", "vegetable"]},
            {"name": "Shirataki Rice", "reason": "Very low calorie, konjac-based", "health_tags": ["low_calorie", "low_carb"]},
        ],
    },
    "cheese": {
        "healthier": [
            {"name": "Low-fat Cheese", "reason": "Reduced fat content", "health_tags": ["low_fat", "high_protein"]},
            {"name": "Cottage Cheese", "reason": "High protein, lower calories", "health_tags": ["high_protein", "low_calorie"]},
            {"name": "Feta Cheese", "reason": "Lower calories than hard cheeses", "health_tags": ["lower_calorie", "flavorful"]},
        ],
        "vegan": [
            {"name": "Nutritional Yeast", "reason": "Cheesy flavor, B vitamins", "health_tags": ["vegan", "vitamin_b", "savory"]},
            {"name": "Cashew Cheese", "reason": "Creamy, plant-based", "health_tags": ["vegan", "plant_based", "nut_based"]},
            {"name": "Vegan Cheese", "reason": "Commercial dairy-free cheese", "health_tags": ["vegan", "dairy_free"]},
        ],
        "low_calorie": [
            {"name": "Part-skim Mozzarella", "reason": "Lower fat and calories", "health_tags": ["low_calorie", "low_fat"]},
            {"name": "Cottage Cheese", "reason": "High protein, filling", "health_tags": ["low_calorie", "high_protein"]},
        ],
    },
}

# ==================== API Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """API Root endpoint"""
    return {
        "message": "Welcome to Smart Recipe Engine API",
        "version": "1.0.0",
        "endpoints": {
            "recipes": "/recipes",
            "search": "/recipes/search",
            "substitutions": "/ingredients/substitute",
            "alternatives": "/recipes/{id}/alternatives"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        await mongodb_client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# ==================== Recipe Endpoints ====================

@app.post("/recipes", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["Recipes"])
async def create_recipe(recipe: RecipeCreate):
    """Create a new recipe"""
    try:
        collection = get_recipes_collection()
        
        recipe_dict = recipe.model_dump()
        result = await collection.insert_one(recipe_dict)
        
        created_recipe = await collection.find_one({"_id": result.inserted_id})
        return recipe_helper(created_recipe)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating recipe: {str(e)}"
        )

@app.get("/recipes", response_model=List[dict], tags=["Recipes"])
async def get_all_recipes(limit: int = 50):
    """Get all recipes (limited to avoid overload)"""
    try:
        collection = get_recipes_collection()
        recipes = []
        
        async for recipe in collection.find().limit(limit):
            recipes.append(recipe_helper(recipe))
        
        return recipes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recipes: {str(e)}"
        )

@app.get("/recipes/{recipe_id}", response_model=dict, tags=["Recipes"])
async def get_recipe_by_id(recipe_id: str):
    """Get a specific recipe by ID"""
    try:
        collection = get_recipes_collection()
        
        if not ObjectId.is_valid(recipe_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recipe ID format"
            )
        
        recipe = await collection.find_one({"_id": ObjectId(recipe_id)})
        
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with ID {recipe_id} not found"
            )
        
        return recipe_helper(recipe)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recipe: {str(e)}"
        )

@app.post("/recipes/search", response_model=List[dict], tags=["Recipes"])
async def search_recipes(search_request: RecipeSearchRequest):
    """
    Search recipes by ingredients, diet tags, and max calories
    """
    try:
        collection = get_recipes_collection()
        
        # Build query
        query = {}
        
        # Search by ingredients (if any ingredient matches)
        if search_request.ingredients:
            ingredient_patterns = [
                {"ingredients.name": {"$regex": ing, "$options": "i"}}
                for ing in search_request.ingredients
            ]
            query["$or"] = ingredient_patterns
        
        # Filter by diet tags (must have all specified tags)
        if search_request.diet_tags:
            query["diet_tags"] = {"$all": search_request.diet_tags}
        
        # Filter by max calories
        if search_request.max_calories:
            query["calories"] = {"$lte": search_request.max_calories}
        
        # Execute query
        recipes = []
        async for recipe in collection.find(query).limit(50):
            recipes.append(recipe_helper(recipe))
        
        return recipes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching recipes: {str(e)}"
        )

@app.delete("/recipes/{recipe_id}", tags=["Recipes"])
async def delete_recipe(recipe_id: str):
    """Delete a recipe by ID"""
    try:
        collection = get_recipes_collection()
        
        if not ObjectId.is_valid(recipe_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recipe ID format"
            )
        
        result = await collection.delete_one({"_id": ObjectId(recipe_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with ID {recipe_id} not found"
            )
        
        return {"message": f"Recipe {recipe_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting recipe: {str(e)}"
        )

# ==================== Substitution Endpoints ====================

@app.post("/ingredients/substitute", response_model=SubstituteResponse, tags=["Substitutions"])
async def get_ingredient_substitute(request: SubstituteRequest):
    """
    Get smart ingredient substitutions based on goal
    """
    ingredient_lower = request.ingredient.lower().strip()
    goal_lower = request.goal.lower().strip()
    
    # Check if ingredient exists in our knowledge base
    if ingredient_lower not in INGREDIENT_SUBSTITUTIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No substitutions found for '{request.ingredient}'. Try: sugar, milk, butter, eggs, cream, flour, rice, cheese"
        )
    
    ingredient_data = INGREDIENT_SUBSTITUTIONS[ingredient_lower]
    
    # Get substitutes for the specified goal
    if goal_lower not in ingredient_data and goal_lower != "any":
        # If goal not found, return healthier options
        substitutes = ingredient_data.get("healthier", [])
    elif goal_lower == "any":
        # Return all substitutes for "any" goal
        substitutes = []
        for goal_type in ingredient_data.values():
            substitutes.extend(goal_type)
        # Remove duplicates based on name
        seen = set()
        unique_substitutes = []
        for sub in substitutes:
            if sub["name"] not in seen:
                seen.add(sub["name"])
                unique_substitutes.append(sub)
        substitutes = unique_substitutes
    else:
        substitutes = ingredient_data[goal_lower]
    
    return SubstituteResponse(
        original=request.ingredient,
        goal=request.goal,
        substitutes=[SubstituteItem(**sub) for sub in substitutes]
    )

# ==================== Healthier Alternatives Endpoint ====================

@app.get("/recipes/{recipe_id}/alternatives", response_model=List[dict], tags=["Alternatives"])
async def get_healthier_alternatives(recipe_id: str):
    """
    Find healthier recipe alternatives with similar ingredients but lower calories
    """
    try:
        collection = get_recipes_collection()
        
        if not ObjectId.is_valid(recipe_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recipe ID format"
            )
        
        # Get the original recipe
        original_recipe = await collection.find_one({"_id": ObjectId(recipe_id)})
        
        if not original_recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with ID {recipe_id} not found"
            )
        
        # Extract ingredient names from original recipe
        original_ingredients = [
            ing["name"].lower() 
            for ing in original_recipe.get("ingredients", [])
        ]
        
        original_calories = original_recipe.get("calories")
        
        if not original_ingredients:
            return []
        
        # Build query to find similar recipes
        query = {
            "_id": {"$ne": ObjectId(recipe_id)},  # Exclude original recipe
            "$or": [
                {"ingredients.name": {"$regex": ing, "$options": "i"}}
                for ing in original_ingredients
            ]
        }
        
        # If original has calories, find recipes with fewer calories
        if original_calories:
            query["calories"] = {"$lt": original_calories}
        
        # Find alternative recipes
        alternatives = []
        async for recipe in collection.find(query).limit(10):
            alternatives.append(recipe_helper(recipe))
        
        # Sort by calories (lowest first) if available
        alternatives.sort(key=lambda x: x.get("calories") or float('inf'))
        
        return alternatives
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding alternatives: {str(e)}"
        )

# ==================== Run Application ====================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🍳 Starting Smart Recipe Engine API")
    print("=" * 60)
    print(f"📊 MongoDB: {MONGODB_URL}")
    print(f"🗄️  Database: {DB_NAME}")
    print(f"📦 Collection: {RECIPES_COLLECTION}")
    print("=" * 60)
    print("🚀 Server running at: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
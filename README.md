# 🍳 Recipe Recommendation & Ingredient Substitution Engine

## 📌 Project Summary

The **Recipe Recommendation & Ingredient Substitution Engine** is an AI-powered web application that helps users find recipes based on available ingredients and provides suitable ingredient substitutions and healthier alternatives.

The system combines **AI-based semantic similarity, recipe data, nutrition information, FastAPI, and MongoDB Atlas** to provide intelligent recipe recommendations.

---

## 🎯 Problem Statement

Traditional recipe platforms mainly provide keyword-based recipe searches and have limited support for ingredient substitution and personalized health recommendations.

This project aims to build a system that can:

- Recommend recipes based on available ingredients
- Suggest suitable ingredient substitutes
- Provide healthier alternatives
- Support personalized recipe recommendations
- Use nutrition information for better suggestions

---

## 🔬 Research Gap

Existing recipe platforms lack contextual intelligence for:

- Ingredient substitution
- Health-based recipe adjustments
- Semantic similarity between ingredients
- Personalized recipe recommendations

---

## 🧠 Proposed AI Approach

The system can use:

- **Word2Vec / GloVe**
- **Sentence Transformers**
- **Cosine Similarity**
- **Ingredient co-occurrence**
- **Graph-based relationships / GNN**

## Basic workflow:

🏗️ System Architecture
                            USER
                │
                ▼
      ┌──────────────────┐
      │  HTML/CSS/JS     │
      │    Frontend      │
      └────────┬─────────┘
               │
             REST API
               │
               ▼
      ┌──────────────────┐
      │     FastAPI      │
      │     Backend      │
      └────────┬─────────┘
               │
        ┌──────┴───────┐
        ▼              ▼
 ┌─────────────┐ ┌─────────────┐
 │ AI / NLP    │ │  MongoDB    │
 │ Recommendation│ │   Atlas    │
 └─────────────┘ └─────────────┘
 
## ✨ Main Features

🔐 User Login
🏠 Dashboard
🔎 Recipe Search
🥕 Ingredient Substitution
❤️ Healthier Alternatives
🍽️ Recipe Recommendations
📊 Nutrition Information
🧠 AI-based Similarity

## 🛠️ Technologies Used

Frontend  : HTML, CSS, JavaScript
Backend   : Python, FastAPI, Uvicorn
Database  : MongoDB Atlas
AI / NLP  : Word2Vec, GloVe, Sentence Transformers
Tools     : VS Code, Git, GitHub

## 📁 Project Structure

recipe-ai/
│
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   ├── search.html
│   ├── substitutions.html
│   ├── recipes.html
│   ├── styles.css
│   └── app.js
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
└── README.md

## ⚙️ Working

Recipe Recommendation
User enters ingredients
        ↓
FastAPI receives request
        ↓
MongoDB searches recipes
        ↓
Similarity / recommendation logic
        ↓
Recommended recipes displayed
Ingredient Substitution
User selects ingredient
        ↓
Similarity / substitution logic
        ↓
Alternative ingredients
        ↓
Healthier options displayed

## 🗄️ Database

MongoDB Atlas stores:

Recipes
Ingredients
Nutrition Information
Users
Substitutions

## 🚀 Project Outcome

The project provides a simple and intelligent platform for discovering recipes, replacing unavailable ingredients, and finding healthier alternatives.

It can later be extended with personalized recommendations, Sentence-BERT embeddings, GNN-based recommendations, allergy detection, calorie-based recommendations, and image-based ingredient recognition.

## 📌 Project Summary

Recipe Recommendation & Ingredient Substitution Engine is a smart recipe management system that combines AI, NLP, nutrition data, FastAPI, and MongoDB Atlas to provide personalized recipe recommendations and intelligent ingredient substitutions.
```text
Recipe Dataset
      ↓
Ingredient Extraction
      ↓
Embeddings / Similarity
      ↓
Ingredient Relationships
      ↓
Recipe Recommendation
      ↓
Substitution & Healthier Alternatives

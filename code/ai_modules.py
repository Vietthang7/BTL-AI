import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import NearestNeighbors

# Đường dẫn để lưu mô hình
MODEL_PATH = 'models/'
os.makedirs(MODEL_PATH, exist_ok=True)

# 1. Phân loại tin nhắn với Naive Bayes
class MessageClassifier:
    def __init__(self):
        self.vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 2))
        self.classifier = MultinomialNB()
        self.categories = []
        self.is_trained = False
        
    def train(self, messages, categories):
        """Huấn luyện mô hình phân loại tin nhắn"""
        self.categories = list(set(categories))
        X = self.vectorizer.fit_transform(messages)
        self.classifier.fit(X, categories)
        self.is_trained = True
        return self
        
    def predict(self, message):
        """Dự đoán loại tin nhắn"""
        if not self.is_trained:
            return "unknown"
        X = self.vectorizer.transform([message])
        return self.classifier.predict(X)[0]
    
    def save(self, filename='message_classifier.pkl'):
        """Lưu mô hình đã huấn luyện"""
        with open(os.path.join(MODEL_PATH, filename), 'wb') as f:
            pickle.dump({'vectorizer': self.vectorizer, 
                        'classifier': self.classifier,
                        'categories': self.categories,
                        'is_trained': self.is_trained}, f)
    
    def load(self, filename='message_classifier.pkl'):
        """Tải mô hình đã huấn luyện"""
        try:
            with open(os.path.join(MODEL_PATH, filename), 'rb') as f:
                data = pickle.load(f)
                self.vectorizer = data['vectorizer']
                self.classifier = data['classifier']
                self.categories = data['categories']
                self.is_trained = data['is_trained']
            return True
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            return False

# 2. Gợi ý món ăn tương tự với k-NN
class FoodRecommender:
    def __init__(self):
        self.model = NearestNeighbors(n_neighbors=5, algorithm='auto')
        self.food_names = []
        self.food_vectors = None
        self.ingredient_to_idx = {}
        self.is_trained = False
        
    def _create_feature_vectors(self, foods_with_ingredients):
        """Tạo vector đặc trưng cho mỗi món ăn dựa trên nguyên liệu"""
        # Tạo từ điển nguyên liệu
        all_ingredients = set()
        for _, ingredients in foods_with_ingredients.items():
            all_ingredients.update(ingredients)
        
        self.ingredient_to_idx = {ing: i for i, ing in enumerate(sorted(all_ingredients))}
        num_ingredients = len(self.ingredient_to_idx)
        
        # Tạo vector đặc trưng cho mỗi món ăn
        food_vectors = np.zeros((len(foods_with_ingredients), num_ingredients))
        food_names = []
        
        for i, (food_name, ingredients) in enumerate(foods_with_ingredients.items()):
            food_names.append(food_name)
            for ingredient in ingredients:
                idx = self.ingredient_to_idx.get(ingredient)
                if idx is not None:
                    food_vectors[i, idx] = 1
                    
        return np.array(food_names), food_vectors
    
    def train(self, foods_with_ingredients):
        """Huấn luyện mô hình gợi ý món ăn"""
        self.food_names, self.food_vectors = self._create_feature_vectors(foods_with_ingredients)
        self.model.fit(self.food_vectors)
        self.is_trained = True
        return self
    
    def recommend_similar(self, food_name, n=3):
        """Gợi ý các món ăn tương tự dựa trên nguyên liệu"""
        if not self.is_trained:
            return []
            
        try:
            # Tìm vị trí của món ăn trong danh sách
            food_idx = np.where(self.food_names == food_name)[0][0]
            
            # Tìm các món ăn gần nhất
            distances, indices = self.model.kneighbors([self.food_vectors[food_idx]])
            
            # Trả về tên các món ăn tương tự (bỏ qua món đầu tiên vì đó chính là món được chọn)
            similar_foods = [self.food_names[idx] for idx in indices[0][1:n+1]]
            return similar_foods
        
        except (IndexError, ValueError):
            return []
    
    def recommend_from_ingredients(self, ingredients, n=5):
        """Gợi ý món ăn dựa trên danh sách nguyên liệu có sẵn"""
        if not self.is_trained:
            return []
            
        # Tạo vector nguyên liệu
        ingredient_vector = np.zeros(len(self.ingredient_to_idx))
        for ing in ingredients:
            idx = self.ingredient_to_idx.get(ing.lower())
            if idx is not None:
                ingredient_vector[idx] = 1
                
        # Tìm các món ăn phù hợp nhất
        distances, indices = self.model.kneighbors([ingredient_vector])
        
        # Trả về tên các món ăn phù hợp
        recommended_foods = [self.food_names[idx] for idx in indices[0][:n]]
        return recommended_foods
    
    def save(self, filename='food_recommender.pkl'):
        """Lưu mô hình đã huấn luyện"""
        with open(os.path.join(MODEL_PATH, filename), 'wb') as f:
            pickle.dump({'model': self.model,
                        'food_names': self.food_names,
                        'food_vectors': self.food_vectors,
                        'ingredient_to_idx': self.ingredient_to_idx,
                        'is_trained': self.is_trained}, f)
    
    def load(self, filename='food_recommender.pkl'):
        """Tải mô hình đã huấn luyện"""
        try:
            with open(os.path.join(MODEL_PATH, filename), 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.food_names = data['food_names']
                self.food_vectors = data['food_vectors']
                self.ingredient_to_idx = data['ingredient_to_idx']
                self.is_trained = data['is_trained']
            return True
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            return False
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
        self.vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 2)) # chuyen đổi tin nhắn thành vector đặc trưng phân tích ở cấp độ từ và xem xét cả từ đơn và từ đôi
        self.classifier = MultinomialNB() # Thuật toán Naive Bayes đa thức , phù hợp cho loại văn bản
        self.categories = [] # Khai báo loại intent rỗng ban đầu
        self.is_trained = False  # Đánh dấu là chưa được huấn luyện
        
    def train(self, messages, categories):
        """Huấn luyện mô hình phân loại tin nhắn"""
        self.categories = list(set(categories)) # Tạo danh sách loại intent duy nhất từ categories
        X = self.vectorizer.fit_transform(messages) # Học từ điển và chuyển đổii tin nhắn thành messages đặc trưng
        self.classifier.fit(X, categories) # Huấn luyện mô hình Naive Bayes trên dữ liệu đã chuyển đổi
        self.is_trained = True # Cập nhật thành công khi được huaấn luyện
        return self
        
    def predict(self, message):
        """Dự đoán loại tin nhắn"""
        if not self.is_trained:
            return "unknown" # Nếu mô hình chưa được huấn luyện, trả về "unknown"
        X = self.vectorizer.transform([message]) #Chuyển đổi tin nhắn thành vector đặc trưng với từ điển đã học
        return self.classifier.predict(X)[0] # Trả về kết quả dự đoán đầu tiên
    
    #Tạo từ điển chứa tất cả trạng thái cần thiết: vectorizer, classifier, categories và is_trained
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
        self.model = NearestNeighbors(n_neighbors=5, algorithm='auto') # Tìm kiếm 5 món ăn gần nhất , tự động chọn thuật toán láng giềng tối ưu
        # Brute Force:

        # Tính khoảng cách tới tất cả điểm dữ liệu
        # Phù hợp với dữ liệu nhỏ hoặc có số chiều rất cao
        # Độ phức tạp: O(d × n) với d là số chiều, n là số điểm dữ liệu
        # KD Tree:

        # Cấu trúc dữ liệu phân cấp chia không gian thành các vùng nhỏ hơn
        # Phù hợp với dữ liệu có số chiều thấp (thường < 20)
        # Độ phức tạp truy vấn: O(log n) trong trường hợp tốt
        # Ball Tree:

        # Tương tự KD Tree nhưng sử dụng các siêu cầu để phân chia không gian
        # Hiệu quả hơn với dữ liệu có số chiều cao hơn KD Tree
        # Vẫn bị ảnh hưởng bởi "lời nguyền của chiều cao" nhưng ít hơn so với KD Tree
        self.food_names = [] # Danh sách tên món ăn
        self.food_vectors = None # Ma trận đặc trưng của các món ăn dựa trên nguyên liệu
        self.ingredient_to_idx = {} #Từ điển ánh xạ tên nguyên liệu sang chỉ số
        self.is_trained = False # Đánh dấu mô hình chưa được huấn luyện
        
    def _create_feature_vectors(self, foods_with_ingredients): # _ thể hiện đây là hàm nội bộ, không nên gọi trực tiếp từ bên ngoài
        """Tạo vector đặc trưng cho mỗi món ăn dựa trên nguyên liệu"""
        # Tạo từ điển nguyên liệu
        all_ingredients = set() 
        # foods_with_ingredients là từ điển chứa tên món ăn và danh sách nguyên liệu
        for _, ingredients in foods_with_ingredients.items():
            all_ingredients.update([ing.lower().strip() for ing in ingredients])  # Chuẩn hóa nguyên liệu về chữ thường và loại bỏ khoảng trắng
        
        self.ingredient_to_idx = {ing: i for i, ing in enumerate(sorted(all_ingredients))} # Sắp xếp theo nguyên liệu thứ tự bảng chữ cái và đánh số từ 0 đến n-1 cho mõi nguyên liệu
        num_ingredients = len(self.ingredient_to_idx)
        
        # Tạo vector đặc trưng cho mỗi món ăn
        food_vectors = np.zeros((len(foods_with_ingredients), num_ingredients)) # Ma trận 0 với kích thước (số món ăn x số nguyên liệu)
        food_names = []
        
        for i, (food_name, ingredients) in enumerate(foods_with_ingredients.items()):
            food_names.append(food_name)
            for ingredient in ingredients:
                idx = self.ingredient_to_idx.get(ingredient.lower().strip())  # Chuẩn hóa nguyên liệu
                if idx is not None:
                    food_vectors[i, idx] = 1
#         Với mỗi món ăn, đánh số thứ tự i và lưu tên vào food_names
# Với mỗi nguyên liệu của món, tìm chỉ số tương ứng trong từ điển
# Đánh dấu giá trị 1 tại vị trí (i, idx) trong ma trận food_vectors            
                    
        return np.array(food_names), food_vectors
    
    def train(self, foods_with_ingredients):
        """Huấn luyện mô hình gợi ý món ăn"""
        self.food_names, self.food_vectors = self._create_feature_vectors(foods_with_ingredients)
        self.model.fit(self.food_vectors) #Mô hình k-NN xây dựng cấu trúc dữ liệu nội bộ để tìm kiếm nhanh các điểm gần nhất 
        self.is_trained = True
        return self
    
    def _string_similarity(self, str1, str2):
        """Tính độ tương đồng giữa hai chuỗi"""
        # Độ tương đồng dựa trên số ký tự chung
        str1_set = set(str1)
        str2_set = set(str2)
        common = str1_set & str2_set
        return len(common) / max(len(str1_set), len(str2_set))




    def recommend_similar(self, food_name, n=3):
        """Gợi ý các món ăn tương tự dựa trên nguyên liệu"""
        if not self.is_trained:
            return []
            
        try:
            # Tìm vị trí của món ăn trong danh sách (không phân biệt hoa/thường)
            food_idx = np.where(np.char.lower(self.food_names) == food_name.lower())[0][0]
            
            # Tìm các món ăn gần nhất
            distances, indices = self.model.kneighbors([self.food_vectors[food_idx]]) # CHọn K MÓN ĐẦU TIÊN DO các món này có khoảng cách nhỏ nhất dùng của scikit-learn
            
            # Trả về tên các món ăn tương tự (bỏ qua món đầu tiên vì đó chính là món được chọn)
            similar_foods = [self.food_names[idx] for idx in indices[0][1:n+1]]
            return similar_foods
        # indices[0] là mảng chỉ số của các món gần nhất
        # indices[0][1:n+1] bỏ qua món đầu tiên (vì đó chính là món được tìm) và lấy n món tiếp theo
        # Chuyển đổi chỉ số thành tên món ăn

        
        except (IndexError, ValueError):
            # Nếu không tìm thấy món ăn chính xác, tìm món có tên gần giống nhất
            food_name_lower = food_name.lower()
            food_similarities = [self._string_similarity(food_name_lower, name.lower()) 
                               for name in self.food_names]
            
            # Nếu có ít nhất một món có độ tương đồng > 0.5
            if max(food_similarities) > 0.5:
                most_similar_idx = np.argsort(food_similarities)[-n:][::-1]  # Sắp xếp giảm dần
                return [self.food_names[idx] for idx in most_similar_idx]
            
            # Nếu không tìm thấy món ăn có tên tương tự, trả về các món ăn phổ biến
            popular_foods = ["Phở bò", "Bún chả", "Cơm tấm"]
            existing_popular = [food for food in popular_foods if food in self.food_names]
            if existing_popular:
                return existing_popular[:n]
            return []
    
    def recommend_from_ingredients(self, ingredients, n=3):
        """Gợi ý món ăn dựa trên danh sách nguyên liệu có sẵn"""
        if not self.is_trained:
            return []
        
        # Chuẩn hóa danh sách nguyên liệu
        clean_ingredients = [ing.lower().strip() for ing in ingredients]
            
        # Tạo vector nguyên liệu
        ingredient_vector = np.zeros(len(self.ingredient_to_idx))
        matched_ingredients = 0
        
        for ing in clean_ingredients:
            idx = self.ingredient_to_idx.get(ing)
            if idx is not None:
                ingredient_vector[idx] = 1
                matched_ingredients += 1
        
        # Nếu không có nguyên liệu nào khớp, trả về danh sách trống
        if matched_ingredients == 0:
            return []
                
        # Tìm các món ăn phù hợp nhất
        distances, indices = self.model.kneighbors([ingredient_vector])
        
        # Trả về tên các món ăn phù hợp kèm theo điểm tương đồng
        similarity_scores = 1 - distances[0]  # Chuyển khoảng cách thành độ tương đồng
        
        # Lọc ra những món có độ tương đồng đủ cao (>0.3)
        recommended_foods = []
        for i, idx in enumerate(indices[0][:n]):
            if similarity_scores[i] > 0.3:
                recommended_foods.append(self.food_names[idx])
        
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
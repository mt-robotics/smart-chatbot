# NLP Concepts Documentation

## TF-IDF Vectorization

### What is TF-IDF?
**TF-IDF (Term Frequency-Inverse Document Frequency)** is a numerical method to convert text into numbers that machine learning algorithms can understand. It measures how important a word is to a document within a collection of documents.

### Formula Breakdown:
- **TF (Term Frequency)**: How often a word appears in a document
- **IDF (Inverse Document Frequency)**: How rare/common a word is across all documents
- **TF-IDF = TF × IDF**

### Why Use TF-IDF?
1. **Converts text to numbers**: ML algorithms need numbers, not words
2. **Highlights important words**: Common words like "the", "and" get low scores
3. **Context-aware**: Same word gets different importance in different contexts
4. **Simple but effective**: Works well for text classification tasks

### How TF-IDF Works (Step-by-Step):

**Step 1: Collect All Text**
We gather all the sentences we want to analyze:
- "I want to cancel my order"
- "Where is my order status" 
- "I want to buy a product"

**Step 2: Find All Unique Words**
The system looks through all sentences and makes a list of every unique word:
- Words found: ['buy', 'cancel', 'is', 'my', 'order', 'product', 'status', 'to', 'want', 'where']

**Step 3: Count Word Frequency in Each Sentence**
For each sentence, count how many times each word appears:
- Sentence 1: "cancel" appears 1 time, "order" appears 1 time, "buy" appears 0 times
- Sentence 2: "where" appears 1 time, "order" appears 1 time, "cancel" appears 0 times
- Sentence 3: "buy" appears 1 time, "product" appears 1 time, "cancel" appears 0 times

**Step 4: Calculate How Rare Each Word Is**
Words that appear in many sentences are common (less important):
- "order" appears in 2 out of 3 sentences → somewhat common
- "cancel" appears in 1 out of 3 sentences → more unique/important

**Step 5: Create Final Scores**
Multiply frequency by rarity to get TF-IDF scores:
- Common words get lower scores
- Rare words that appear frequently in a sentence get higher scores

**Step 6: Convert to Number Matrix**
Each sentence becomes a list of numbers representing word importance:
```python
# Example result
Sentence 1: [0.0,  0.85, 0.0,  0.3,  0.3,  0.0,  0.0,  0.3,  0.3,  0.0 ]
#           [buy, cancel, is,  my,  order, product, status, to, want, where]
```

### Code Example:
```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Step 1: Our sentences
documents = [
    "I want to cancel my order",
    "Where is my order status", 
    "I want to buy a product"
]

# Steps 2-6: TF-IDF does all the math for us
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)

# See the results
print("Words found:", vectorizer.get_feature_names_out())
print("Number matrix:")
print(tfidf_matrix.toarray())
```

### Real Example from Our Chatbot:
```python
# In our NLP engine
texts = ["I want to cancel", "Where is my order", "I want to buy"]
X = self.vectorizer.fit_transform(texts)

# "cancel" gets high score in first document
# "order" gets high score in second document  
# "buy" gets high score in third document
```

---

## Naive Bayes Classification

### What is Naive Bayes?
**Naive Bayes** is a probabilistic machine learning algorithm that predicts the category of text based on the probability of words appearing in each category. It's called "naive" because it assumes all words are independent (which isn't true, but works well anyway).

### Why Use Naive Bayes?
1. **Fast training**: Learns quickly from small datasets
2. **Good with text**: Excellent for text classification tasks
3. **Handles multiple classes**: Can classify into many categories
4. **Probabilistic**: Gives confidence scores, not just predictions
5. **Works with sparse data**: Perfect for TF-IDF vectors

### How Naive Bayes Works (Step-by-Step):

**Step 1: Prepare Training Examples**
We show the computer examples of sentences and their correct categories:
- "I want to cancel my order" → Label: "cancel_order"
- "Cancel my purchase" → Label: "cancel_order"  
- "Where is my order" → Label: "order_status"
- "Order status please" → Label: "order_status"

**Step 2: Convert Text to Numbers**
Use TF-IDF to turn each sentence into a list of numbers (as explained above).

**Step 3: Learn Patterns**
The computer analyzes the numbers and notices patterns:
- Sentences with high "cancel" scores usually belong to "cancel_order"
- Sentences with high "status" scores usually belong to "order_status"
- It calculates probabilities for each word in each category

**Step 4: Store the Learning**
The computer remembers these patterns:
- "If I see the word 'cancel', there's an 85% chance it's 'cancel_order'"
- "If I see the word 'status', there's a 90% chance it's 'order_status'"

**Step 5: Make Predictions on New Text**
When a new sentence comes in: "I need to cancel"

**Step 6: Convert New Text to Numbers**
Use the same TF-IDF process to turn the new sentence into numbers.

**Step 7: Calculate Probabilities**
For each possible category, calculate the probability:
- Probability of "cancel_order": 87%
- Probability of "order_status": 10%  
- Probability of "product_inquiry": 3%

**Step 8: Pick the Winner**
Choose the category with the highest probability: "cancel_order" (87% confidence)

### Code Example:
```python
from sklearn.naive_bayes import MultinomialNB

# Step 1: Training examples (already converted to numbers by TF-IDF)
X = tfidf_matrix  # The number lists from TF-IDF
y = ["cancel_order", "order_status", "product_inquiry"]  # The correct labels

# Steps 3-4: Train the classifier to learn patterns
classifier = MultinomialNB()
classifier.fit(X, y)  # "Learn from these examples"

# Steps 5-8: Predict new text
new_text = ["I want to cancel my purchase"]
new_numbers = vectorizer.transform(new_text)  # Convert to numbers

prediction = classifier.predict(new_numbers)  # "What category is this?"
confidence = classifier.predict_proba(new_numbers)  # "How sure are you?"

print("Prediction:", prediction[0])  # "cancel_order"
print("Confidence:", max(confidence[0]))  # 0.87 (87% sure)
```

### Real Example from Our Chatbot:
```python
# In our classify_intent method
def classify_intent(self, text):
    processed_text = self.preprocess_text(text)
    
    # Convert to TF-IDF
    X = self.vectorizer.transform([processed_text])
    
    # Predict intent
    intent = self.intent_classifier.predict(X)[0]
    
    # Get confidence
    confidence = max(self.intent_classifier.predict_proba(X)[0])
    
    return intent, confidence
```

---

## How They Work Together in Our Chatbot

### Step 1: Training Phase
```python
# Training data
training_texts = [
    "I want to cancel my order",
    "Cancel my purchase", 
    "Where is my order",
    "Order status please"
]
training_labels = ["cancel_order", "cancel_order", "order_status", "order_status"]

# Convert text to TF-IDF vectors
X = vectorizer.fit_transform(training_texts)

# Train Naive Bayes
classifier.fit(X, training_labels)
```

### Step 2: Prediction Phase
```python
# New user message
user_message = "I need to cancel"

# Convert to TF-IDF using same vectorizer
user_tfidf = vectorizer.transform([user_message])

# Classify intent
intent = classifier.predict(user_tfidf)[0]  # "cancel_order"
confidence = max(classifier.predict_proba(user_tfidf)[0])  # 0.89
```

### Why This Combination Works:
1. **TF-IDF** converts "I need to cancel" into numbers like [0.0, 0.85, 0.0, 0.67, ...]
2. **Naive Bayes** looks at these numbers and says "These numbers look most like 'cancel_order' examples I've seen"
3. **Result**: Correctly identifies the user wants to cancel something

### Strengths:
- Fast and efficient
- Works well with small datasets
- Interpretable results

### Limitations:
- Simple approach - doesn't understand context deeply
- Assumes words are independent
- Can be confused by similar intents

This is why we added keyword-based rules as a hybrid approach to improve accuracy!
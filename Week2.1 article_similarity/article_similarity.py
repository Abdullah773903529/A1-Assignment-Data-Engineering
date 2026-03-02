import csv
import numpy as np
import string
import re
import os
import pickle  

def clean_text(text):

    text = text.lower()
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    text = re.sub(r'\d+', '', text)
    return text.split()

def load_articles(filename='articles.csv'):
    if not os.path.exists(filename):
        print(f" الملف {filename} غير موجود. الرجاء التأكد من وجوده.")
        return None

    articles = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            articles.append({
                'id': int(row['id']),
                'title': row['title'],
                'words': clean_text(row['content'])
            })
    print(f" تم تحميل {len(articles)} مقالة.")
    return articles

def build_vocabulary(articles):

    vocab = set()
    for art in articles:
        vocab.update(art['words'])
    return sorted(vocab)

def build_vectors(articles, vocab):
    word_to_idx = {w: i for i, w in enumerate(vocab)}
    vectors = np.zeros((len(articles), len(vocab)), dtype=int)
    for i, art in enumerate(articles):
        for w in set(art['words']):
            vectors[i, word_to_idx[w]] = 1
    return vectors

def compute_similarity_matrix(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    sim = np.dot(vectors, vectors.T) / np.dot(norms, norms.T)
    return np.clip(sim, -1.0, 1.0)

def save_similarity_matrix(sim_matrix, filename='similarity_matrix.pkl'):

    with open(filename, 'wb') as f:
        pickle.dump(sim_matrix, f)
    print(f" تم حفظ مصفوفة التشابه في '{filename}'")

def find_top_similar(article_id, articles, sim_matrix, top_n=3):


    id_to_idx = {art['id']: i for i, art in enumerate(articles)}
    if article_id not in id_to_idx:
        return None, "المعرف غير موجود."

    idx = id_to_idx[article_id]
    similarities = sim_matrix[idx].copy()
    similarities[idx] = -np.inf
    top_indices = np.argsort(similarities)[::-1][:top_n]
    top_ids = [articles[i]['id'] for i in top_indices]
    top_titles = [articles[i]['title'] for i in top_indices]
    top_scores = [similarities[i] for i in top_indices]
    return list(zip(top_ids, top_titles, top_scores)), None

def show_common_words(articles, id1, id2):

    art1 = next((a for a in articles if a['id'] == id1), None)
    art2 = next((a for a in articles if a['id'] == id2), None)
    if not art1 or not art2:
        print(" أحد المعرفات غير صحيح.")
        return

    common = set(art1['words']) & set(art2['words'])
    print(f"\n الكلمات المشتركة بين '{art1['title']}' و '{art2['title']}':")
    if common:
        print(f"   عدد الكلمات: {len(common)}")
        print("   " + ", ".join(sorted(common)))
    else:
        print("   لا توجد كلمات مشتركة.")

def main():

    articles = load_articles('articles.csv')
    if articles is None:
        return


    vocab = build_vocabulary(articles)
    vectors = build_vectors(articles, vocab)
    sim_matrix = compute_similarity_matrix(vectors)


    save_similarity_matrix(sim_matrix)

    print("\n" + "="*50)
    print(" أهلاً بك في برنامج تحليل تشابه المقالات")
    print("="*50)

    while True:
        print("\n القائمة المتاحة:")
        for art in articles:
            print(f"  {art['id']}: {art['title']}")

        user_input = input("\n أدخل رقم المقالة المراد تحليلها (أو اكتب 'خروج' للإنهاء): ").strip()
        if user_input.lower() in ['خروج', 'exit', 'quit']:
            print(" وداعاً!")
            break

        try:
            target_id = int(user_input)
        except ValueError:
            print(" الرجاء إدخال رقم صحيح.")
            continue

        result, error = find_top_similar(target_id, articles, sim_matrix)
        if error:
            print(f"{error}")
            continue

        print(f"\n أكثر 3 مقالات تشابهاً مع المقالة {target_id}:")
        for rank, (art_id, title, score) in enumerate(result, 1):
            print(f"   {rank}. {title} (معرف {art_id}) - درجة التشابه: {score:.4f}")

        # سؤال المستخدم إذا أراد رؤية الكلمات المشتركة
        see_common = input("\n هل تريد رؤية الكلمات المشتركة مع إحداها؟ (أدخل معرف المقالة أو اضغط Enter للاستمرار): ").strip()
        if see_common:
            try:
                common_id = int(see_common)
                show_common_words(articles, target_id, common_id)
            except ValueError:
                print("لم يتم عرض الكلمات (إدخال غير صحيح).")

if __name__ == "__main__":
    main()
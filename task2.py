import re
import requests
import matplotlib.pyplot as plt
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from bs4 import BeautifulSoup


def map_function(chunk):
    word_count = Counter(re.findall(r"\w+", chunk.lower()))
    return word_count


def reduce_function(results):
    final_result = Counter()
    for result in results:
        final_result += result
    return final_result


def mapreduce(data, map_func, reduce_func, num_processes):
    chunk_size = len(data) // num_processes
    chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        mapped = executor.map(map_func, chunks)

    reduced = reduce_func(mapped)
    return reduced


def visualize_top_words(word_freq, top_n=10):
    top_words = word_freq.most_common(top_n)
    words, frequencies = zip(*top_words)
    plt.figure(figsize=(10, 6))
    plt.bar(words, frequencies, color="skyblue")
    plt.xlabel("Words")
    plt.ylabel("Frequency")
    plt.title(f"Top {top_n} Most Common Words")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def main(url, num_processes=4, top_n=10):
    response = requests.get(url)
    text = response.text
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text()

    word_freq = mapreduce(text, map_function, reduce_function, num_processes)

    visualize_top_words(word_freq, top_n=top_n)


if __name__ == "__main__":
    url = "https://uk.wikipedia.org/wiki/%D0%A1%D0%BA%D0%BE%D0%BC%D0%BE%D1%80%D0%BE%D1%85%D0%B8"
    main(url)

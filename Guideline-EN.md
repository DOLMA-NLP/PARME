# **Machine Translation for Languages in the Middle East**

Sina Ahmadi \- University of Zurich ([sina.ahmadi@uzh.ch](mailto:sina.ahmadi@uzh.ch))  
Created on June 25th, 2024  
Last modified on July 16, 2024

This document is available in the following languages as well:

- [Farsi](Guideline-FA.md)
- [Central Kurdish](Guideline-CKB.md)

<p align="center" width="100%">
    <img width="60%" img src="https://dolma-nlp.github.io/assets/img/ME_languages.png" alt="CORDI">
</p>

## **Goal**

The objective of this task is to create parallel corpora for under-represented languages in the Middle East. Given the current language landscape in the region, many languages lack essential tools and resources that enable speakers to use technology in their language. This collective initiative aims to change that landscape and empower speakers to employ technology in their everyday life. This project paves the way for more developments with some applications such as spelling error correction, machine translation, morphosyntactic processing and ultimately, more ambitious ones like automatic speech recognition.

## **Task Description**

Our starting point is a parallel corpus. A parallel corpus contains a pair of sentences in two languages that are translations. By collecting a large number of sentences, i.e. thousands of translations, we can leverage the existing technologies or create new ones to build a machine translation system where sentences in your language can be translated into any other language in the world. 

Provided with a parallel corpus, your task is to translate sentences into your language. Although the process can seem easy at the first glance, it may represent a few challenges such as the followings:

1. **Writing and orthography:** Some languages have a longer oral tradition than a written one. As such, it is not very clear how to deal with them when written. On the other hand, some languages might have an orthography, but are not popular among the speakers. You, as an expert in your language, can decide on what is the best for writing your language. As a general rule, if there is an orthography for your language, regardless of its popularity, that might be the best way to write your language.   
2. **Standard language:** Standardization is a process that needs time, an authority to enforce and years of training and education. Many languages might not have a standardized variety. If so, follow the dialect that you are most comfortable with and know the best.  
3. **Vocabulary:** It is crucial that your translation contains **native words** and not engulfed with foreignisms or loanwords. Although in everyday life, modern speakers might use certain words from other languages, like Arabic, Persian or Turkish, your task should reflect the potential of your language the most and not how everyday people use it. For instance, a Kurdish speaker might naturally use the Arabic word "تسلط" (*tasallot*), which is a loanword from Arabic (or through Persian), while not using the native Kurdish word "دەسەڵات" for the same meaning. You should always prefer the native words to the loanwords. As a rule of thumb, ask yourself: "would my monolingual grandfather use "تسلط" or its native alternative".  
4. **Terminologies:** Coming up with native translations is not always easy, particularly when it comes to terminologies or specific vocabulary. How to translate "hard disk", "computer" or "extortion" in my native language? There is a simple rule: if you think that someone already coined a word in your language for specific terms (like "خێراکار" in Kurdish for "computer"), use it. If not, you can borrow words from other languages, i.e. you can simply use "computer" in your language. This borrowing should conform with your orthography so that a code-switching doesn't happen. This is an example in Gilaki where for "computer" is borrowed: "اولين الکترؤنيکي ديجيتال **کامپيۊتر** بؤ گه دؤومي جهاني جنگˇ مئن تؤسعه پىدا واگۊد." Note that the word "کامپيۊتر" follows the orthography used in Gilaki even though it is a borrowing from English (through Persian).  
5. **External resources:** If your language has a dictionary, you can consult to help you in the translation task. 

### **Workflow**

You are provided with a spreadsheet like this:

| English Translation | Persian Translation | Your Translation |
| ----- | ----- | ----- |
| this is the kitchen | اینجا آشپزخانه است |  |
| I have nothing for you to do. | من کاری ندارم به شما بدم. |  |
| she hastened from the room. | با شتاب از اطاق بیرون رفت. |  |

* In the shared spreadsheet, the "main" spreadsheet contains parallel sentences to be translated by you. The sentences are provided in two languages (English and another language). Translate from the one that you are most comfortable with. You can hide the column of the other language.  
* If one these conditions is met, you can skip the sentence and move to the next one:  
  * **The sentence doesn’t make sense**  
  * **The sentence has spelling errors, code-switching (mixing words in two or more different languages)**  
  * **The sentence contains named entities (like name of people or locations)**  
* Sentences with blank translations will be ignored at the end.  
* If you use a specific word or term, you can add them to the sheet called "my\_dictionary". This can be useful to create a dictionary for your language as well.

## **Your contribution**

We are all doing this project following our love for the language and our passion to develop language technology. What is sure is that your work, regardless of the amount, will be acknowledged and appreciated. If you can make substantial contributions, co-authorship in a scientific paper is possible. Please reach out if you’re interested.

## **Frequently Asked Questions:**

1. There is no standard orthography for writing my language. How should I write my language?  
2. **Please use a writing system that makes sense to you and follow it *consistently*. Zazaki, for example, is written in an orthography on Wikipedia other than the Kurdish one; you can decide which one to use – and only use that one.**  
3. Should I compare the translation of the two different languages before translating into my language?   
   **If it helps clarify the meaning of a specific word, yes\! Otherwise, there is no need. The provided parallel corpus contains the same sentences in two languages.**   
4. There is an error in the sentence that I am translating from. Should I fix it?  
   **There is no need to change the original sentences. If they are not correct, simply skip them (but don’t delete the row). If, for any reason, translating a given sentence is not possible in your language, you can skip them. At the end, only non-empty cells are considered as valid translations.**

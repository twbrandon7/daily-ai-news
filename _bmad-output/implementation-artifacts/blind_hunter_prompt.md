# Blind Hunter Prompt

Invoke the `bmad-review-adversarial-general` skill on this diff:

```diff
diff --git a/src/publisher.py b/src/publisher.py
index da92c7f..7ff2efd 100644
--- a/src/publisher.py
+++ b/src/publisher.py
@@ -44,7 +44,7 @@ def _validate_highlight_terms(english: str, translated: str) -> None:
 
 async def generate_daily_highlight(articles: list[dict]) -> str | None:
     """
-    Generate a daily highlight summary in English from a list of articles using Google ADK and gemini-2.0-flash.
+    Generate a daily highlight summary in English from a list of articles using Google ADK and gemini-3.5-flash-lite.
     """
     if not articles:
         return None
@@ -61,7 +61,7 @@ async def generate_daily_highlight(articles: list[dict]) -> str | None:
 
     try:
         agent = LlmAgent(
-            model="gemini-2.0-flash",
+            model="gemini-3.5-flash-lite",
             name="daily_highlight_generator",
             instruction=DAILY_HIGHLIGHT_PROMPT,
         )
@@ -108,7 +108,7 @@ async def generate_daily_highlight(articles: list[dict]) -> str | None:
 
 async def translate_highlight(highlight: str) -> str | None:
     """
-    Translate an English highlight into Traditional Chinese (Taiwan) using Google ADK and gemini-2.0-flash.
+    Translate an English highlight into Traditional Chinese (Taiwan) using Google ADK and gemini-3.5-flash-lite.
     """
     if not highlight:
         return None
@@ -118,7 +118,7 @@ async def translate_highlight(highlight: str) -> str | None:
 
     try:
         agent = LlmAgent(
-            model="gemini-2.0-flash",
+            model="gemini-3.5-flash-lite",
             name="highlight_translator",
             instruction=HIGHLIGHT_TRANSLATE_PROMPT,
         )
diff --git a/src/summarizer.py b/src/summarizer.py
index c9ecd8b..8aba233 100644
--- a/src/summarizer.py
+++ b/src/summarizer.py
@@ -119,7 +119,7 @@ async def summarize_article(url: str, body: str, title: str) -> dict | None:
 
     try:
         agent = LlmAgent(
-            model="gemini-2.0-flash",
+            model="gemini-3.5-flash-lite",
             name="summarizer",
             instruction=SUMMARIZE_PROMPT,
         )
diff --git a/src/translator.py b/src/translator.py
index 2a5089a..0b66283 100644
--- a/src/translator.py
+++ b/src/translator.py
@@ -163,7 +163,7 @@ async def translate_summary(url: str, summary: dict) -> dict | None:
 
     try:
         agent = LlmAgent(
-            model="gemini-2.0-flash",
+            model="gemini-3.5-flash-lite",
             name="translator",
             instruction=TRANSLATE_PROMPT,
         )
```

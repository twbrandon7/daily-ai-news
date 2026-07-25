# Blind Hunter Prompt

Invoke the `bmad-review-adversarial-general` skill on this diff:

```diff
diff --git a/src/summarizer.py b/src/summarizer.py
index 528e270..5f5a9c7 100644
--- a/src/summarizer.py
+++ b/src/summarizer.py
@@ -8,15 +8,13 @@ from google.adk.agents import LlmAgent
 from google.adk.runners import Runner
 from google.adk.sessions import InMemorySessionService
 from google.genai import types as genai_types
-from pydantic import BaseModel, Field, ConfigDict
+from pydantic import BaseModel, Field

 class InsightsTradeoffs(BaseModel):
-    model_config = ConfigDict(extra="forbid")
     pros: list[str] = Field(description="Key advantages or positive aspects.")
     cons: list[str] = Field(description="Key drawbacks, limitations, or negative aspects.")

 class ArticleSummary(BaseModel):
-    model_config = ConfigDict(extra="forbid")
     tldr: str = Field(description="One-sentence summary of the article.")
     problem_why: str = Field(description="What problem does this article address and why it matters.")
     solution_how: str = Field(description="How the article solves the problem or what approach is described.")
diff --git a/src/translator.py b/src/translator.py
index 60ca0ce..d2ed083 100644
--- a/src/translator.py
+++ b/src/translator.py
@@ -8,15 +8,13 @@ from google.adk.agents import LlmAgent
 from google.adk.runners import Runner
 from google.adk.sessions import InMemorySessionService
 from google.genai import types as genai_types
-from pydantic import BaseModel, Field, ConfigDict
+from pydantic import BaseModel, Field

 class InsightsTradeoffs(BaseModel):
-    model_config = ConfigDict(extra="forbid")
     pros: list[str] = Field(description="Key advantages or positive aspects.")
     cons: list[str] = Field(description="Key drawbacks, limitations, or negative aspects.")

 class TranslationSummary(BaseModel):
-    model_config = ConfigDict(extra="forbid")
     tldr: str = Field(description="One-sentence summary of the article.")
     problem_why: str = Field(description="What problem does this article address and why it matters.")
     solution_how: str = Field(description="How the article solves the problem or what approach is described.")
```

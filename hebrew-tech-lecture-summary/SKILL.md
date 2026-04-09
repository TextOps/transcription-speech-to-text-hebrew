---
name: hebrew-tech-lecture-summary
description: Summarize Hebrew tech lectures and meetings from transcription files into structured Markdown. Use when the user asks to summarize a transcription, create meeting notes, summarize a lecture/presentation in Hebrew, or mentions סיכום/תמלול/הרצאה.
license: MIT
compatibility: "Designed for Claude Code. No external dependencies required."
metadata:
  version: "1.0.0"
  author: "TextOps"
  tags: "summary, lecture, hebrew, meeting-notes, transcription"
  language: "he"
---

# סיכום הרצאות ופגישות טכניות בעברית

יוצר סיכום מובנה ב-Markdown מתוך קובץ תמלול, בצורה שנותנת ערך מלא למי שלא היה בהרצאה.

## תהליך העבודה

1. קרא את קובץ התמלול (בד"כ `output/transcription_plain.txt`)
2. נתח את התוכן: זהה נושאים, דוברים, שאלות מהקהל, וציטוטים חשובים
3. כתוב את הסיכום לפי המבנה שב-[template.md](template.md)
4. שמור ב-`output/lecture_summary.md`

## אסור בהחלט

**אל תוסיף שום הערה עריכתית שלא מגיעה מהתמלול.**

דוגמאות להערות אסורות:
- "זה הסיכום למי שרצה את התוכן"
- "מי שלא הגיע יכול לשמוע את ההקלטה"
- "הסיכום נכתב על בסיס התמלול בלבד"
- "לפרטים נוספים ניתן לפנות למרצה"
- כל משפט שאינו תוכן ישיר מהתמלול

**עקוב אחר [template.md](template.md) בלבד.** לא מוסיפים, לא מסבירים, לא מגיבים — פשוט כותבים את הסיכום.

---

## כללי כתיבה

### שפה ומונחים
- הסיכום **בעברית**, אבל מושגי tech ותכנות נשארים **באנגלית**
- דוגמאות: production, deploy, PR, build, MCP, workspace, branch, commit, Docker image, rollout, pipeline, CI/CD, code review, unit test, integration test, API, endpoint, repository
- שמות כלים ומוצרים באנגלית: Cursor, Jenkins, Argo, Splunk, Jira, GitHub

### הנחיות שלב-אחרי-שלב
כשיש תהליך או רצף פעולות, השתמש בחיצים:

```
git clone --> פתיחת workspace ב-Cursor --> הרצת build --> deploy ל-QA
```

### מבנה הסיכום
הסיכום חייב להיות **כרונולוגי** -- לפי הסדר שבו הדברים נאמרו בהרצאה. ראה [template.md](template.md) למבנה המלא.

### עקרונות תוכן
- **ערך מלא** -- מי שפספס את ההרצאה צריך לקבל את כל התוכן המהותי
- **קונקרטי** -- דוגמאות ספציפיות, לא הכללות
- **שאלות מהקהל** -- כל שאלה ותשובה, זה חלק חשוב מהערך
- **ציטוטים** -- משפטים חזקים ומדויקים שנאמרו בהרצאה
- אל תמציא תוכן שלא נאמר בהרצאה
- אם חלק מהתמלול לא ברור -- דלג עליו, אל תנחש

### חשוב: אין הערות עריכה
הסיכום הוא **תוכן בלבד**. אין להוסיף:
- הקדמות או מסקנות שלך
- הפניות להקלטה, למרצה, או למקורות חיצוניים
- הסברים על איך הסיכום נכתב
- כל דבר שאינו חלק מהמבנה ב-[template.md](template.md)

# 🛡️ מערכת ניהול תורנויות

אפליקציית Next.js לניהול תורנויות עם Supabase ו-Vercel.

---

## 📦 הכנת Supabase

1. היכנס ל-[supabase.com](https://supabase.com) וצור פרויקט חדש.
2. עבור ל-**SQL Editor** ורוץ את ה-SQL הבא:

```sql
-- טבלת עמדות
CREATE TABLE positions (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  sort_order INT NOT NULL DEFAULT 0
);

-- טבלת שיבוצים
CREATE TABLE assignments (
  id SERIAL PRIMARY KEY,
  week_monday DATE NOT NULL,
  position TEXT NOT NULL,
  soldier_name TEXT NOT NULL,
  UNIQUE (week_monday, position)
);

-- הרשאות פתוחות (לאנונימי — מתאים לפרויקט פנימי)
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE assignments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "allow_all_positions" ON positions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_assignments" ON assignments FOR ALL USING (true) WITH CHECK (true);
```

3. עבור ל-**Project Settings > API** והעתק:
   - `Project URL`
   - `anon public key`

---

## 🚀 פריסה על Vercel

### שיטה 1 — דרך GitHub (מומלצת)

1. העלה את הפרויקט ל-GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USER/tornot.git
git push -u origin main
```

2. היכנס ל-[vercel.com](https://vercel.com) > **New Project** > בחר את ה-repo.
3. הוסף את משתני הסביבה (**Environment Variables**):
   - `NEXT_PUBLIC_SUPABASE_URL` = ה-URL מ-Supabase
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = ה-anon key מ-Supabase
   - `NEXT_PUBLIC_ADMIN_PASSWORD` = הסיסמה שתרצה (ברירת מחדל: `1234`)
4. לחץ **Deploy** ✅

### שיטה 2 — Vercel CLI

```bash
npm i -g vercel
vercel
```
ואז הוסף את משתני הסביבה בממשק Vercel.

---

## 💻 פיתוח מקומי

```bash
# התקנת חבילות
npm install

# העתק והגדר משתני סביבה
cp .env.example .env.local
# ערוך את .env.local עם הערכים שלך

# הפעלת שרת פיתוח
npm run dev
```

הפרויקט יפתח בכתובת: http://localhost:3000

---

## 🔐 כניסת מנהל

- לחץ על לשונית **שיבוץ** או **עמדות**
- הזן את הסיסמה (ברירת מחדל: `1234`)
- שנה את הסיסמה דרך משתנה הסביבה `NEXT_PUBLIC_ADMIN_PASSWORD`

---

## 🗂️ מבנה הפרויקט

```
tornot/
├── app/
│   ├── api/
│   │   ├── assignments/route.ts   ← API: שיבוצים
│   │   └── positions/route.ts     ← API: עמדות
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx                   ← האפליקציה הראשית
├── lib/
│   ├── supabase.ts               ← חיבור Supabase
│   ├── dates.ts                  ← פונקציות תאריך
│   └── defaults.ts               ← עמדות ברירת מחדל
├── .env.example
└── package.json
```

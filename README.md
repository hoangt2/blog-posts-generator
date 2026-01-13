# Blog Posts Generator

A Python CLI tool that generates daily MDX blog posts for Finnish language learners (A1-A2 level) using Gemini AI.

## Features

- 📚 Extracts content from Finnish textbooks (Suomen mestari 1, Suomi sujuvaksi 1)
- 🤖 AI-powered blog post generation with Gemini
- 🖼️ AI-generated illustrations for each post
- 📅 Daily scheduling with no duplicate dates
- 🎯 Intelligent topic tracking to avoid repetition
- 🔍 SEO-optimized MDX output

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

3. **Extract book content (first time only):**
   ```bash
   python main.py extract-books
   ```

## Usage

### Generate a blog post for tomorrow
```bash
python main.py generate
```

### Generate for a specific date
```bash
python main.py generate --date 2026-01-15
```

### Generate multiple posts (next N days)
```bash
python main.py generate --days 7
```

### View topic history
```bash
python main.py topics --list
```

### Force a specific topic
```bash
python main.py generate --topic "Finnish Numbers"
```

## Output

Blog posts are generated in the `output/` directory:
```
output/
├── 2026-01-14-finnish-greetings.mdx
├── 2026-01-15-numbers-in-finnish.mdx
└── images/
    ├── 2026-01-14-finnish-greetings.png
    └── 2026-01-15-numbers-in-finnish.png
```

## Project Structure

```
blog-posts-generator/
├── books/              # Finnish textbook PDFs
├── output/             # Generated blog posts
├── data/               # Topic tracking & cached extractions
├── src/                # Source modules
├── main.py             # CLI entry point
└── requirements.txt
```

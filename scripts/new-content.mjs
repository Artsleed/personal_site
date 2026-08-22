#!/usr/bin/env node
// Scaffolds a new blog post or project write-up with correct frontmatter.
// Usage: npm run new-post -- "Title" ["description"]
//        npm run new-project -- "Title" ["description"]

import { writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

const [, , type, title, description] = process.argv;

if (type !== 'blog' && type !== 'project') {
  console.error('Usage: npm run new-post -- "Title" ["description"]');
  console.error('       npm run new-project -- "Title" ["description"]');
  process.exit(1);
}

const command = type === 'project' ? 'new-project' : 'new-post';

if (!title) {
  console.error(`Missing title.\nUsage: npm run ${command} -- "Title" ["description"]`);
  process.exit(1);
}

const slug = title
  .toLowerCase()
  .trim()
  .replace(/['"]/g, '')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

if (!slug) {
  console.error('Could not derive a filename from that title - try something with letters or numbers in it.');
  process.exit(1);
}

const collectionDir = type === 'project' ? 'projects' : 'blog';
const dir = join(root, 'src', 'content', collectionDir);
const filePath = join(dir, `${slug}.md`);

if (existsSync(filePath)) {
  console.error(`${filePath} already exists - pick a different title, or edit it directly.`);
  process.exit(1);
}

mkdirSync(dir, { recursive: true });

const today = new Date().toISOString().slice(0, 10);
const finalDescription = description || 'TODO: add a description.';

const frontmatter = `---
title: ${JSON.stringify(title)}
date: ${today}
description: ${JSON.stringify(finalDescription)}
---

Write your ${type === 'project' ? 'project write-up' : 'post'} here.
`;

writeFileSync(filePath, frontmatter, 'utf8');

console.log(`Created ${filePath}`);
console.log(`Run "npm run dev" and visit /${collectionDir}/${slug} to preview it.`);

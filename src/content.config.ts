import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    date: z.date(),
    description: z.string(),
  }),
});

const projects = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    date: z.date(),
    description: z.string(),
    stack: z.string().default('TBD'),
    status: z.string().default('In progress'),
    role: z.string().default('Solo'),
    started: z.string().default('TBD'),
    processNote: z.string().optional(),
    aside: z.string().optional(),
  }),
});

export const collections = { blog, projects };
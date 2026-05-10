import { createClient } from '@supabase/supabase-js';

const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(url, key);

export type Assignment = {
  id?: number;
  week_monday: string; // ISO date YYYY-MM-DD
  position: string;
  soldier_name: string;
};

export type Position = {
  id?: number;
  name: string;
  sort_order: number;
};

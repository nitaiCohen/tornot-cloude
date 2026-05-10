import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';
import { DEFAULT_POSITIONS } from '@/lib/defaults';

export async function GET() {
  const { data, error } = await supabase
    .from('positions')
    .select('*')
    .order('sort_order');

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  // Seed defaults if empty
  if (!data || data.length === 0) {
    const seed = DEFAULT_POSITIONS.map((name, i) => ({ name, sort_order: i }));
    await supabase.from('positions').insert(seed);
    return NextResponse.json(seed.map((p, i) => ({ id: i + 1, ...p })));
  }

  return NextResponse.json(data);
}

export async function POST(req: NextRequest) {
  const { name } = await req.json();
  const { data: existing } = await supabase.from('positions').select('sort_order').order('sort_order', { ascending: false }).limit(1);
  const next_order = existing && existing.length > 0 ? existing[0].sort_order + 1 : 0;

  const { data, error } = await supabase
    .from('positions')
    .insert({ name, sort_order: next_order })
    .select();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

export async function DELETE(req: NextRequest) {
  const { id } = await req.json();
  const { error } = await supabase.from('positions').delete().eq('id', id);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true });
}

export async function PUT(req: NextRequest) {
  // Reset to defaults
  await supabase.from('positions').delete().neq('id', 0);
  const seed = DEFAULT_POSITIONS.map((name, i) => ({ name, sort_order: i }));
  const { data, error } = await supabase.from('positions').insert(seed).select();
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

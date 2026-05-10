import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(req: NextRequest) {
  const week = req.nextUrl.searchParams.get('week');
  const all = req.nextUrl.searchParams.get('all');

  let query = supabase.from('assignments').select('*').order('position');
  if (week) query = query.eq('week_monday', week);

  const { data, error } = await query;
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { week_monday, position, soldier_name } = body;

  // Upsert by week+position
  const { data, error } = await supabase
    .from('assignments')
    .upsert({ week_monday, position, soldier_name }, { onConflict: 'week_monday,position' })
    .select();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

export async function DELETE(req: NextRequest) {
  const { week_monday, position } = await req.json();
  const { error } = await supabase
    .from('assignments')
    .delete()
    .eq('week_monday', week_monday)
    .eq('position', position);

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true });
}

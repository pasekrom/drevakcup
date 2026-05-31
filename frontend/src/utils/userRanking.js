/**
 * Pořadí uživatelů: celkem A+B, pak tiebreak dle pravidel turnaje.
 */
export function compareUsersByRanking(a, b) {
  const ta = Number(a.points_part_a ?? 0) + Number(a.points_part_b ?? 0)
  const tb = Number(b.points_part_a ?? 0) + Number(b.points_part_b ?? 0)
  if (tb !== ta) return tb - ta

  const pa = Number(a.points_part_a ?? 0)
  const pb = Number(b.points_part_a ?? 0)
  if (pb !== pa) return pb - pa

  const wa = a.tiebreak_winner_guessed ? 1 : 0
  const wb = b.tiebreak_winner_guessed ? 1 : 0
  if (wb !== wa) return wb - wa

  const ea = Number(a.tiebreak_exact_7_count ?? 0)
  const eb = Number(b.tiebreak_exact_7_count ?? 0)
  if (eb !== ea) return eb - ea

  const fa = a.tiebreak_final_b_guessed ? 1 : 0
  const fb = b.tiebreak_final_b_guessed ? 1 : 0
  if (fb !== fa) return fb - fa

  return String(a.display_name || '').localeCompare(String(b.display_name || ''), 'cs', {
    sensitivity: 'base',
  })
}

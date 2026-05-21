<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Pravidla</h2>
    
    <div class="card space-y-6">
      <div>
        <h3 class="text-xl font-bold mb-3">Bodování - Část A (Tipy na zápasy)</h3>
        <p class="text-gray-700 mb-3">
          V části A se tipuje <strong>výsledek v základní hrací době</strong>.
        </p>
        <ul class="list-disc list-inside space-y-2 text-gray-700">
          <li><strong>7 bodů:</strong> Přesný výsledek zápasu</li>
          <li><strong>3 body:</strong> Správný výsledek (výhra/remíza/prohra)</li>
        </ul>
      </div>
      
      <div>
        <h3 class="text-xl font-bold mb-3">Bodování - Část B (Speciální tipy)</h3>
        <ul class="list-disc list-inside space-y-2 text-gray-700">
          <li>Tým, který vstřelí nejvíce branek (dle pravidel IIHF): <strong>12 bodů</strong></li>
          <li>Tým, který obdrží nejméně branek (dle pravidel IIHF): <strong>12 bodů</strong></li>
          <li>Tým, který vstřelí první branku: <strong>3 body</strong></li>
          <li>Tým, který vstřelí poslední branku na MS: <strong>12 bodů</strong></li>
          <li>Tým, který sestoupí ze skupiny A: <strong>6 bodů</strong></li>
          <li>Tým, který sestoupí ze skupiny B: <strong>6 bodů</strong></li>
          <li>Počet remíz/prodloužení za celé MS: <strong>24 bodů</strong></li>
          <li>Nejvíce branek na MS v jednom utkání (počet dohromady za oba týmy): <strong>12 bodů</strong></li>
          <li>Tým 1, který se utká o bronz: <strong>12 bodů</strong></li>
          <li>Tým 2, který se utká o bronz: <strong>12 bodů</strong></li>
          <li>Finalista: <strong>16 bodů</strong></li>
          <li>Vítěz: <strong>24 bodů</strong></li>
          <li>Vítěz každé skupiny (A, B): <strong>9 bodů</strong></li>
          <li>2. - 4. místo každé skupiny (A, B): <strong>6 bodů</strong></li>
          <li>Střelec 1. gólu ČR: <strong>12 bodů</strong></li>
          <li>Střelec posledního gólu ČR: <strong>12 bodů</strong></li>
        </ul>
      </div>
      
      <div>
        <h3 class="text-xl font-bold mb-3">Část C</h3>
        <p class="text-gray-700">
          Celkový součet bodů z části A a části B.
        </p>
      </div>

      <div>
        <details class="rounded-lg border border-gray-200 bg-gray-50">
          <summary class="cursor-pointer select-none px-4 py-3 font-bold text-gray-900">
            Kritéria při rovnosti bodů
          </summary>
          <div class="px-4 pb-4 text-gray-700">
            <ul class="list-disc list-inside space-y-2">
              <li>Lepší umístění v 1. části</li>
              <li>Uhádnutí celkového vítěze</li>
              <li>Vyšší počet přesných typů za 7 bodů v 1. části</li>
              <li>Uhádnutí druhého finalisty</li>
            </ul>
          </div>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  cup: {
    type: Object,
    required: true,
  },
})
</script>

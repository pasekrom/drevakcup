<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Pravidla</h2>
    
    <div class="card space-y-6">
      <div>
        <h3 class="text-xl font-bold mb-3">Bodování - Část A (Tipy na zápasy)</h3>
        <ul class="list-disc list-inside space-y-2 text-gray-700">
          <li><strong>7 bodů:</strong> Přesný výsledek zápasu</li>
          <li><strong>3 body:</strong> Správný výsledek (výhra/remíza/prohra)</li>
        </ul>
      </div>
      
      <div>
        <h3 class="text-xl font-bold mb-3">Bodování - Část B (Speciální tipy)</h3>
        <ul class="list-disc list-inside space-y-2 text-gray-700">
          <li><strong>24 body:</strong> Vítěz turnaje</li>
          <li><strong>16 bodů:</strong> Každý finalista</li>
          <li><strong>12 bodů:</strong> Každý tým v boji o bronz</li>
          <li><strong>12 bodů:</strong> Český střelec prvního/posledního gólu</li>
          <li><strong>12 bodů:</strong> Nejvíce branek v jednom zápase</li>
          <li><strong>9 bodů:</strong> Vítěz skupiny</li>
          <li><strong>6 bodů:</strong> 2.-4. místo ve skupině</li>
          <li><strong>12 bodů:</strong> Tým s nejvíce/nejméně brankami</li>
          <li><strong>3 body:</strong> Tým s prvním gólem turnaje</li>
          <li><strong>12 bodů:</strong> Tým s posledním gólem turnaje</li>
          <li><strong>6 bodů:</strong> Tým sestupující ze skupiny</li>
          <li><strong>24 bodů:</strong> Počet remíz/prodloužení</li>
        </ul>
      </div>
      
      <div>
        <h3 class="text-xl font-bold mb-3">Část C</h3>
        <p class="text-gray-700">
          Celkový součet bodů z části A a části B.
        </p>
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

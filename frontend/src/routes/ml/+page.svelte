<script>
// @ts-nocheck

	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { onMount } from 'svelte';
    import { PUBLIC_BACKEND_URL } from '$env/static/public';


    let homeTeam = '';
    let awayTeam = '';
    let homeGoalsHT = '';
    let awayGoalsHT = '';
    let roundSel = '';

    const teams = [
        "Atlas",
        "Atletico San Luis",
        "Atlético San Luis",
        "Club America",
        "Club Queretaro",
        "Club Tijuana",
        "Cruz Azul",
        "FC Juarez",
        "Guadalajara Chivas",
        "Jaguares de Chiapas",
        "Leon",
        "León",
        "Lobos Buap",
        "Mazatlán",
        "Monarcas",
        "Monterrey",
        "Necaxa",
        "Pachuca",
        "Puebla",
        "Santos Laguna",
        "Tigres UANL",
        "Toluca",
        "U.N.A.M. - Pumas",
        "Veracruz"
    ];

    const round = [
        "Apertura - 1",
        "Apertura - 2",
        "Apertura - 3",
        "Apertura - 4",
        "Apertura - 5",
        "Apertura - 6",
        "Apertura - 7",
        "Apertura - 8",
        "Apertura - 9",
        "Apertura - 10",
        "Apertura - 11",
        "Apertura - 12",
        "Apertura - 13",
        "Apertura - 14",
        "Apertura - 15",
        "Apertura - 16",
        "Apertura - 17",
        "Apertura - 18",
        "Apertura - 19",
        "Apertura - Reclasificación",
        "Apertura - Quarter-finals",
        "Apertura - Semi-finals",
        "Apertura - Final",
        "Apertura - Finals",
        "Apertura - Play-offs",
        "Clausura - 1",
        "Clausura - 2",
        "Clausura - 3",
        "Clausura - 4",
        "Clausura - 5",
        "Clausura - 6",
        "Clausura - 7",
        "Clausura - 8",
        "Clausura - 9",
        "Clausura - 10",
        "Clausura - 11",
        "Clausura - 12",
        "Clausura - 13",
        "Clausura - 14",
        "Clausura - 15",
        "Clausura - 16",
        "Clausura - 17",
        "Clausura - Reclasificacion",
        "Clausura - Quarter-finals",
        "Clausura - Semi-finals",
        "Clausura - Final",
        "Clausura - Finals",
        "Clausura - Play-offs"
    ];

    function handleHTLocal(e) {
        const v = e.target.value;
        if (v === '') { homeGoalsHT = ''; return; }
        const n = Number(v);
        if (Number.isFinite(n)) homeGoalsHT = String(Math.max(0, Math.floor(n)));
    }

    function handleHTAway(e) {
        const v = e.target.value;
        if (v === '') { awayGoalsHT = ''; return; }
        const n = Number(v);
        if (Number.isFinite(n)) awayGoalsHT = String(Math.max(0, Math.floor(n)));
    }

    $: isValidInt = (v) => v !== '' && Number.isInteger(Number(v)) && Number(v) >= 0;
    $: canSubmit = homeTeam !== '' && awayTeam !== '' && homeTeam !== awayTeam && roundSel !== '' && isValidInt(homeGoalsHT) && isValidInt(awayGoalsHT);

    let predHome = null;
    let predAway = null;
    let loading = false;
    let error = null;

    async function predict() {
        loading = true;
        error = null;
        predHome = null;
        predAway = null;

        if (!canSubmit) {
            error = 'Selecciona equipos distintos, una jornada válida y proporciona goles de medio tiempo como enteros no negativos.';
            loading = false;
            return;
        }

        try {
            const response = await fetch(`${PUBLIC_BACKEND_URL}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    home_team: homeTeam,
                    away_team: awayTeam,
                    round: roundSel,
                    home_goals_half_time: parseInt(homeGoalsHT),
                    away_goals_half_time: parseInt(awayGoalsHT)
                })
            });

            if (!response.ok) {
                throw new Error('Fallo al predecir');
            }

            const data = await response.json();
            predHome = data.home_goals;
            predAway = data.away_goals;

        } catch (err) {
            // @ts-ignore
            error = err.message;
        } finally {
            loading = false;
        }
    }
</script>

<Header title="Machine Learning 🤖" />

<section class="min-h-screen bg-gray-100 py-10">
  <div class="container mx-auto px-4">
    <div class="max-w-xl mx-auto bg-white shadow-md rounded-xl p-6">
      <h2 class="text-2xl font-semibold text-gray-800 mb-6">Predicción de marcador</h2>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Equipo Local</label>
        <select bind:value={homeTeam} class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="" disabled>Selecciona equipo</option>
          {#each teams as team}
            <option value={team}>{team}</option>
          {/each}
        </select>
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Equipo Visitante</label>
        <select bind:value={awayTeam} class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="" disabled>Selecciona equipo</option>
          {#each teams as team}
            <option value={team}>{team}</option>
          {/each}
        </select>
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Jornada / Fase</label>
        <select bind:value={roundSel} class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="" disabled>Selecciona jornada</option>
          {#each round as r}
            <option value={r}>{r}</option>
          {/each}
        </select>
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Goles Local (Medio Tiempo)</label>
        <input type="number" min="0" step="1" bind:value={homeGoalsHT} on:input={handleHTLocal} class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-1">Goles Visitante (Medio Tiempo)</label>
        <input type="number" min="0" step="1" bind:value={awayGoalsHT} on:input={handleHTAway} class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      <button
        on:click={predict}
        disabled={loading || !canSubmit}
        class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
      >
        {loading ? 'Calculando...' : 'Predecir'}
      </button>

      {#if predHome !== null && predAway !== null}
        <div class="mt-6 p-4 bg-green-100 border border-green-300 rounded-lg text-green-800">
          Resultado Predicho — Local: {predHome} | Visitante: {predAway}
        </div>
      {/if}

      {#if error}
        <div class="mt-4 p-4 bg-red-100 border border-red-300 rounded-lg text-red-800">
          {error}
        </div>
      {/if}
    </div>
  </div>
</section>

<Footer />
<script lang="ts">
	import type { Snippet } from 'svelte';
	import './layout.css';
	import ExplorerTree from '$lib/components/ui/ExplorerTree.svelte';
	import SiteFooter from '$lib/components/ui/SiteFooter.svelte';
	import StatusBar from '$lib/components/ui/StatusBar.svelte';
	import WindowFrame from '$lib/components/ui/WindowFrame.svelte';
	import {
		explorerItems,
		explorerStatus,
		footerContacts,
		footerCredit,
		footerLicenses
	} from '$lib/data/arcade';

	import myComputerIcon from '$lib/assets/images/mycomputer.png';

	interface Props {
		children: Snippet;
	}

	let { children }: Props = $props();
</script>

<div class="p-5 pb-8 md:px-4" id="top">
	<div class="mx-auto grid max-w-[800px] gap-4.5">
		<WindowFrame title="GenAI Arcade" icon={myComputerIcon} class="w-full">
			<div
				class="grid [grid-template-columns:minmax(220px,28%)_minmax(0,1fr)] gap-1.5 max-[760px]:grid-cols-1"
			>
				<ExplorerTree items={explorerItems} />

				<div class="max-h-96 overflow-auto bg-white p-2.5 bevel-sunken">
					{@render children()}
				</div>
			</div>

			<StatusBar left={explorerStatus.left} right={explorerStatus.right} />
		</WindowFrame>

		<WindowFrame title="Content" class="w-full">
			<div class="bg-white p-2 bevel-sunken">
				{@render children()}
			</div>
		</WindowFrame>

		<SiteFooter contacts={footerContacts} licenses={footerLicenses} credit={footerCredit} />
	</div>
</div>

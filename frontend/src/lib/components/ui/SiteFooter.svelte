<script lang="ts">
	import type { FooterContact, FooterCredit, FooterLicense } from '$lib/data/arcade';

	interface Props {
		contacts: FooterContact[];
		licenses: FooterLicense[];
		credit: FooterCredit;
	}

	let { contacts, licenses, credit }: Props = $props();
</script>

<footer class="mt-7.5 mb-2.5 text-xs" id="footer">
	<p class="mb-3 text-center">
		If you want to learn more about the GenAI Arcade tool, contact
		{#each contacts as contact, index (`${contact.email}-${index}`)}
			{contact.name}:
			<a class="text-[#24244a]" href={`mailto:${contact.email}`}>{contact.email}</a>, {contact.role}{index <
			contacts.length - 1
				? ' OR '
				: '.'}
		{/each}
	</p>

	{#each licenses as license (license.label)}
		<p class="mb-3 text-center">
			<strong>{license.label}:</strong>
			{license.text}
			<a class="text-[#24244a]" href={license.href} target="_blank" rel="external noreferrer">
				{license.href}
			</a>
		</p>
	{/each}

	<p class="m-0 text-center">
		{credit.label} created by
		<a class="text-[#24244a]" href={credit.href} target="_blank" rel="external noreferrer">
			{credit.name}
		</a>
		| Code licensed under
		<a class="text-[#24244a]" href={credit.licenseHref} target="_blank" rel="external noreferrer">
			{credit.licenseLabel}
		</a>
	</p>
</footer>

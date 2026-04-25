<script lang="ts">
	import type { FooterContact, FooterCredit, FooterLicense } from '$lib/data/arcade';

	interface Props {
		contacts: FooterContact[];
		licenses: FooterLicense[];
		credit: FooterCredit;
	}

	let { contacts, licenses, credit }: Props = $props();
</script>

<footer class="site-footer" id="footer">
	<p>
		If you want to learn more about the GenAI Arcade tool, contact
		{#each contacts as contact, index (`${contact.email}-${index}`)}
			{contact.name}:
			<a href={`mailto:${contact.email}`}>{contact.email}</a>, {contact.role}{index <
			contacts.length - 1
				? ' OR '
				: '.'}
		{/each}
	</p>

	{#each licenses as license (license.label)}
		<p>
			<strong>{license.label}:</strong>
			{license.text}
			<a href={license.href} target="_blank" rel="external noreferrer">{license.href}</a>
		</p>
	{/each}

	<p>
		{credit.label} created by
		<a href={credit.href} target="_blank" rel="external noreferrer">{credit.name}</a>
		| Code licensed under
		<a href={credit.licenseHref} target="_blank" rel="external noreferrer">{credit.licenseLabel}</a>
	</p>
</footer>

<style>
	.site-footer {
		font-size: 12px;
		margin: 30px 0 10px;
	}

	p {
		margin: 0 0 12px;
		text-align: center;
	}

	a {
		color: #24244a;
	}
</style>

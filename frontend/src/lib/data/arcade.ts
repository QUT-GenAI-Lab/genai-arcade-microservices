export interface MenuItem {
	label: string;
	href: string;
	external?: boolean;
}

export interface WindowControl {
	symbol: string;
	label: string;
	href?: string;
	disabled?: boolean;
}

export interface ExplorerTreeItem {
	title: string;
	href?: string;
	icon: string;
	active?: boolean;
	external?: boolean;
	children?: ExplorerTreeItem[];
}

export interface CardItem {
	title: string;
	description: string;
	href: string;
	icon: string;
	eyebrow?: string;
	meta?: string;
	external?: boolean;
}

export interface DesktopNavItem {
	label: string;
	icon: string;
	href: string;
	compact?: boolean;
}

export interface PagerLink {
	label: string;
	href: string;
}

export interface PageSection {
	id?: string;
	title: string;
	paragraphs: string[];
	bullets?: string[];
	quote?: string;
}

export interface FooterContact {
	name: string;
	email: string;
	role: string;
}

export interface FooterLicense {
	label: string;
	text: string;
	href: string;
}

export interface FooterCredit {
	label: string;
	name: string;
	href: string;
	licenseLabel: string;
	licenseHref: string;
}

export interface Category {
	id: string;
	title: string;
	summary: string;
	icon: string;
	games: {
		title: string;
		summary: string;
		href: string;
	}[];
}

import folderIcon from '$lib/assets/images/folder.ico';
import fileIcon from '$lib/assets/images/file.ico';
import type { ResolvedPathname } from '$app/types';
import { base } from '$app/paths';

export const menuItems: MenuItem[] = [
	{ label: 'About Us', href: '#about' },
	{ label: 'Resources', href: 'https://research.qut.edu.au/genailab/', external: true }
];

export const standalonePages: CardItem[] = [
	{
		title: 'How to use the Arcade',
		description:
			'Explains folder-based navigation, recommended paths, and how the games connect across categories.',
		href: '#how-to',
		icon: fileIcon,
		eyebrow: 'Standalone page',
		meta: 'Guide'
	},
	{
		title: 'About Us',
		description:
			'Introduces the QUT Generative AI Lab and the public-facing AI literacy goals behind the Arcade.',
		href: '#about',
		icon: fileIcon,
		eyebrow: 'Standalone page',
		meta: 'Info'
	}
];

export const categories: Category[] = [
	{
		id: 'understanding',
		title: 'Understanding',
		summary: 'Games about how AI “understands” things.',
		icon: folderIcon,
		games: [
			{
				title: 'Word by Word',
				summary:
					'Learn how a language model responds by predicting likely next words rather than checking what is true.',
				href: '#understanding'
			},
			{
				title: 'Sort of Calculator',
				summary:
					'Explore why generative AI struggles with maths and what that reveals about prediction versus knowledge.',
				href: '#understanding'
			},
			{
				title: 'LinkedIn Generator',
				summary:
					'See how AI thrives in formulaic contexts where repeating familiar language patterns works well.',
				href: '#understanding'
			}
		]
	},
	{
		id: 'training',
		title: 'Training',
		summary: 'Games about what AI can learn from data.',
		icon: folderIcon,
		games: [
			{
				title: 'Tone Matters',
				summary:
					'Compare how polite and rude phrasing pulls different response patterns from training data.',
				href: '#training'
			},
			{
				title: 'Speak my Language',
				summary:
					'Probe which languages and forms of expression the model handles well, and which remain uneven.',
				href: '#training'
			},
			{
				title: 'Average Internet',
				summary:
					'Inspect dominant visual patterns in image-model training data through a generated “average internet.”',
				href: '#training'
			}
		]
	},
	{
		id: 'limits',
		title: 'Limits',
		summary: 'Games about AI’s boundaries and constraints.',
		icon: folderIcon,
		games: [
			{
				title: 'Environment',
				summary: 'Highlights the environmental cost of using generative AI systems.',
				href: '#limits'
			},
			{
				title: 'Time Capsule',
				summary:
					'Shows how models are snapshots in time and how training cutoffs shape what they can know.',
				href: '#limits'
			},
			{
				title: 'Short-Term Memory',
				summary:
					'Explores context window limits and why a model can appear to forget recent instructions.',
				href: '#limits'
			},
			{
				title: 'DIY LLM',
				summary:
					'Introduces retrieval-augmented generation and how added context changes practical model behavior.',
				href: '#limits'
			}
		]
	},
	{
		id: 'values',
		title: 'Values',
		summary: 'Games about choices in AI systems.',
		icon: folderIcon,
		games: [
			{
				title: 'Align Me',
				summary:
					'Lets players judge responses to ethical dilemmas and see how feedback changes later output.',
				href: '#values'
			},
			{
				title: 'Milkless',
				summary:
					'Examines safety constraints by pushing on a model that has been instructed to avoid a topic.',
				href: '#values'
			}
		]
	}
];

interface NavigationTreeNode {
	fullPath: string;
	title: string;
	href?: string;
	children?: NavigationTreeNode[];
}

// Convert from flat list of /path/to/page to nested tree structure for explorer navigation
class NavigationTree {
	root: NavigationTreeNode;

	constructor(
		title: string = 'Root',
		private skipPrefix: string = ''
	) {
		this.root = { fullPath: '', title, children: [] };
	}

	addPath(path: string, title: string, href?: string) {
		const cleanPath = path.startsWith(this.skipPrefix) ? path.slice(this.skipPrefix.length) : path;
		const parts = cleanPath.split('/').filter(Boolean);
		let currentNode = this.root;

		for (let i = 0; i < parts.length; i++) {
			const part = parts[i];
			const fullPath = '/' + parts.slice(0, i + 1).join('/');
			let childNode = currentNode.children?.find((child) => child.fullPath === fullPath);

			if (!childNode) {
				childNode = { fullPath, title: part, children: [] };
				currentNode.children = currentNode.children || [];
				currentNode.children.push(childNode);
			}

			currentNode = childNode;
		}

		// Set the title and href on the final node
		currentNode.title = title;
		if (href) {
			currentNode.href = href;
			delete currentNode.children; // Remove children if it's a leaf node
		}
	}
}

const widgets = (() => {
	// Glob the src/routes/widgets for all +page.svelte files and extract title
	const widgetModules = import.meta.glob('/src/routes/widgets/**/+page.svelte', { eager: true });
	console.log('Found widget modules:', widgetModules);
	type Widget = { url: ResolvedPathname; path: string; title: string };
	function parseWidget(path: string): Widget | null {
		// Extract the widget id from the path, e.g.
		// /src/routes/widgets/understanding/word-by-word/+page.svelte => understanding/word-by-word
		const match = path.match(/\/widgets\/(.+)\/\+page\.svelte$/);
		if (!match) {
			console.warn(`Could not parse widget from path: ${path}`);
			return null;
		}
		const id = match[1];
		// Remove any grouping (e.g., (group)/ - including the /) from the id to get a clean URL path
		const cleanId = id.replace(/\([^/]+\)\//g, '');
		const url = `/widgets/${cleanId}` as ResolvedPathname;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		const module = widgetModules[path] as any;
		const title = module?.title || cleanId;
		return { url, path, title };
	}

	const widgets = Object.keys(widgetModules)
		.map(parseWidget)
		.filter((widget): widget is Widget => widget !== null);
	console.log('Parsed widgets:', widgets);
	return widgets;
})();

const widgetTree: ExplorerTreeItem = (() => {
	console.log('Building navigation tree from widgets:', widgets);
	const tree = new NavigationTree('Widgets');
	widgets.forEach((widget) => {
		tree.addPath(widget.url, widget.title, widget.url);
	});
	console.log('Constructed navigation tree:', tree);

	// Convert NavigationTreeNode to ExplorerTreeItem recursively
	function convertNode(node: NavigationTreeNode): ExplorerTreeItem {
		return {
			title: node.title,
			href: `${base}${node.href || ''}`,
			icon: node.children?.length ? folderIcon : fileIcon,
			children: node.children?.map(convertNode)
		};
	}
	tree.root.children![0].title = 'Widgets'; // Rename top-level folder to "All Widgets"
	return convertNode(tree.root.children![0]);
})();

export const explorerItems: ExplorerTreeItem[] = [widgetTree];

export const landingCards: CardItem[] = [
	...standalonePages,
	...categories.map((category) => ({
		title: category.title,
		description: category.summary,
		href: `#${category.id}`,
		icon: category.icon,
		eyebrow: 'Category',
		meta: `${category.games.length} game${category.games.length === 1 ? '' : 's'}`
	}))
];

export const desktopNavItems: DesktopNavItem[] = [
	{ label: 'Home', icon: '⌂', href: '#top', compact: true },
	{ label: 'Browse Sections', icon: '▤', href: '#sections' },
	{ label: 'Start with Understanding', icon: '▶', href: '#overview' }
];

export const communityNote = {
	title: 'Community Note',
	body: 'Execution backends are still being migrated. Some original widgets are not embedded in this shell yet, but layout, navigation, and reusable chrome now live in Svelte components.'
};

export const overviewSections: PageSection[] = [
	{
		id: 'overview',
		title: 'Why we built the GenAI Arcade',
		paragraphs: [
			'Generative AI is everywhere, but most explainers either bury people in jargon, hide environmental and social costs, or turn the technology into science-fiction spectacle.',
			'The Arcade takes different path: playful, critical, and hands-on. Instead of only reading about AI, visitors can poke, test, and stress it through focused games that expose both capabilities and limits.',
			'No coding background required. Curiosity is enough.'
		],
		quote: 'Where do you go to learn about GenAI?'
	},
	{
		title: 'What you gain from understanding GenAI',
		paragraphs: [
			'Understanding model behavior helps people ask sharper questions, decide when not to use AI, and see through inflated marketing claims.',
			'The site frames AI literacy as practical judgment: knowing when prediction is useful, when to verify output, and when lower-impact tools make more sense.'
		],
		bullets: [
			'Better prompting because users understand how pattern-based systems respond.',
			'Environmental responsibility when a simpler tool would do less harm.',
			'Critical awareness of hype, bias, and overclaiming.',
			'More informed participation in decisions about how AI should be used.'
		]
	},
	{
		title: 'Your role in the future of GenAI',
		paragraphs: [
			'The future of generative AI is not fixed. The choices people make about which tools they trust, reject, or reshape matter now.',
			'The Arcade positions public understanding as part of that future-building work, not as passive product adoption.'
		]
	}
];

export const howToSections: PageSection[] = [
	{
		id: 'how-to',
		title: 'How to navigate the Arcade',
		paragraphs: [
			'Arcade v1 used classic desktop metaphor: folders on left, files on right, big navigation buttons below, and windowed content areas in front.',
			'This Svelte extraction keeps those patterns modular so future routes can reuse them without copying old Jekyll includes.'
		],
		bullets: [
			'Open category folders from explorer tree.',
			'Read summaries from cards before jumping into game route.',
			'Use page-level menu bar and footer pager for orientation.',
			'Keep windows visually consistent so navigation feels familiar across routes.'
		]
	},
	{
		title: 'Reusable components identified from v1',
		paragraphs: [
			'The original shell repeated same structural pieces across default and tag layouts. Those pieces are now isolated as Svelte components rather than Liquid includes and long shared stylesheets.'
		],
		bullets: [
			'Window frame with title bar and optional controls.',
			'Desktop navigation button row.',
			'Explorer tree for home, folders, files, and external links.',
			'Card grid for category and landing-page summaries.',
			'Status bar, menu bar, footer pager, and site footer.'
		]
	}
];

export const aboutSections: PageSection[] = [
	{
		id: 'about',
		title: 'About the QUT Generative AI Lab',
		paragraphs: [
			'The site was created by the Generative AI Lab at Queensland University of Technology. The lab combines technical, humanities, and social-science expertise to build more useful and accountable public-facing AI tools.',
			'Its work treats generative AI as social and cultural infrastructure, not only as engineering problem.'
		]
	},
	{
		title: 'Why this project exists',
		paragraphs: [
			'The Arcade was built to make AI literacy accessible, engaging, and empowering. It invites people to examine how systems work, what they can do, and what they should not be trusted to do.',
			'That mission carries into v2: reusable interface pieces should support explainability, not distract from it.'
		]
	}
];

export const footerContacts: FooterContact[] = [
	{
		name: 'Dr Kevin Witzenberger',
		email: 'kevin.witzenberger@qut.edu.au',
		role: 'Research Fellow at QUT’s GenAI Lab'
	},
	{
		name: 'William He',
		email: 'william.he@qut.edu.au',
		role: 'Machine Learning Engineer at QUT’s GenAI Lab'
	}
];

export const footerLicenses: FooterLicense[] = [
	{
		label: 'Content License',
		text: 'All written content, images, and research data are licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).',
		href: 'https://creativecommons.org/licenses/by-nc/4.0/'
	},
	{
		label: 'Code License',
		text: 'All code, scripts, and software are licensed under GNU General Public License v3.0 (GPLv3).',
		href: 'https://www.gnu.org/licenses/gpl-3.0.html'
	}
];

export const footerCredit: FooterCredit = {
	label: 'Windows 95 theme',
	name: 'h01000110 (hi)',
	href: 'http://github.com/h01000110',
	licenseLabel: 'MIT License',
	licenseHref: 'https://github.com/h01000110/h01000110.github.io/blob/master/LICENSE'
};

export const pagerLinks = {
	overview: { previous: null, next: { label: 'How to use the Arcade', href: '#how-to' } },
	howTo: {
		previous: { label: 'GenAI Arcade', href: '#overview' },
		next: { label: 'About Us', href: '#about' }
	},
	about: {
		previous: { label: 'How to use the Arcade', href: '#how-to' },
		next: { label: 'Back to top', href: '#top' }
	}
} satisfies Record<string, { previous: PagerLink | null; next: PagerLink | null }>;

export const explorerStatus = {
	left: `${landingCards.length + categories.reduce((total, category) => total + category.games.length, 0)} object(s)`,
	right: ''
};

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

module.exports = {
  title: 'XL UP Blueprints',
  tagline: '',
  url: 'https://xebialabs.github.io',
  baseUrl: '/xl-up-blueprints/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/digital_ai_deploy.svg',
  organizationName: 'Digital.ai',
  projectName: 'xl-up-blueprints',
  themeConfig: {
    navbar: {
      title: 'XL UP Blueprints',
      logo: {
        alt: 'XL UP Blueprints Digital.ai',
        src: 'img/digital_ai_deploy.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Tutorial',
        },

        {
          href: 'https://github.com/xebialabs/xl-up-blueprints',
          label: 'GitHub',
          position: 'right',
        }
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Tutorial',
              to: '/docs/intro',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/xebialabs/xl-up-blueprints',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} UP Blueprints Digital.ai`,
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js')
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};

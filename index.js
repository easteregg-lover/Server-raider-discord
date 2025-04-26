
// I AM NOT RESPONSIBLE FOR ANY ISSUES, DAMAGES, OR CONSEQUENCES THAT MAY OCCUR FROM THE USE, COPYING, OR DISTRIBUTION OF THIS CODE. BY PROCEEDING, YOU AGREE TO THESE TERMS.
// Made by easteregg_lover (github) [please dont remove this line :3]

const { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

const BOT_TOKEN = 'YOUR_BOT_TOKEN';
const CLIENT_ID = 'YOUR_CLIENT_ID';
const GUILD_ID = 'YOUR_GUILD_ID'; // optional for testing only in one guild
const ALLOWED_USER_ID = 'ID_OF_SOMEONE';

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// Slash commands to register
const commands = [
  new SlashCommandBuilder()
    .setName('embed')
    .setDescription('Repeats text 100x with header format (embed + credit footer)')
    .addStringOption(option =>
      option.setName('input').setDescription('Text to repeat').setRequired(true)),
  new SlashCommandBuilder()
    .setName('embed-without-credits')
    .setDescription('Same as embed but sends embed without credit footer')
    .addStringOption(option =>
      option.setName('input').setDescription('Text to repeat').setRequired(true)),
  new SlashCommandBuilder()
    .setName('normal')
    .setDescription('Same as embed but sends normal message (with credit footer)')
    .addStringOption(option =>
      option.setName('input').setDescription('Text to repeat').setRequired(true)),
  new SlashCommandBuilder()
    .setName('normal-without-credits')
    .setDescription('Same as embed-without-credits but sends normal message (no credit footer)')
    .addStringOption(option =>
      option.setName('input').setDescription('Text to repeat').setRequired(true)),
];

// Register commands once
(async () => {
  const rest = new REST({ version: '10' }).setToken(BOT_TOKEN);
  try {
    console.log('Started refreshing application (/) commands.');
    await rest.put(
      Routes.applicationCommands(CLIENT_ID),
      { body: commands.map(cmd => cmd.toJSON()) }
    );
    console.log('Successfully reloaded application (/) commands.');
  } catch (error) {
    console.error(error);
  }
})();

// Login and interaction handling
client.once('ready', () => {
  console.log(`Logged in as ${client.user.tag}`);
});

client.on('interactionCreate', async interaction => {
  if (interaction.isChatInputCommand()) {
    const input = interaction.options.getString('input');
    const commandName = interaction.commandName;

    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder()
        .setCustomId(`confirm-${commandName}-${input}`)
        .setLabel('Ok!')
        .setStyle(ButtonStyle.Primary)
    );

    await interaction.reply({
      content: 'Are you sure?',
      flags: 1 << 6, // Using flags for ephemeral response
      components: [row],
    });
  }

  if (interaction.isButton()) {
    const [prefix, cmd, input] = interaction.customId.split('-');
    if (!input) return;

    let content = `# ${input.toUpperCase()}\n`.repeat(100);

    switch (cmd) {
      case 'embed':
        content += `\n**Made by** [YOUR SERVER INVITE LINK]`;
        const embedText = new EmbedBuilder()
          .setTitle('Message:')
          .setDescription(content);
        await interaction.reply({ embeds: [embedText] });
        break;
      case 'embed-without-credits':
        const embedWithoutCredits = new EmbedBuilder()
          .setTitle('Message:')
          .setDescription(content);
        await interaction.reply({ embeds: [embedWithoutCredits] });
        break;
      case 'normal':
        content += `\n**Made by** [YOUR SERVER INVITE LINK]`;
        await interaction.reply({ content });
        break;
      case 'normal-without-credits':
        await interaction.reply({ content });
        break;
    }
  }
});

client.login(BOT_TOKEN);


// I AM NOT RESPONSIBLE FOR ANY ISSUES, DAMAGES, OR CONSEQUENCES THAT MAY OCCUR FROM THE USE, COPYING, OR DISTRIBUTION OF THIS CODE. BY PROCEEDING, YOU AGREE TO THESE TERMS.
// Made by easteregg_lover (github) [please dont remove this line :3]

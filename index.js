const { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, InteractionType } = require('discord.js');

const BOT_TOKEN = 'YOUR_BOT_TOKEN';
const CLIENT_ID = 'YOUR_BOT_CLIENT_ID';
const ALLOWED_USER_ID = 'YOUR_USER_ID'; // Replace with the user ID you want to allow

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// Slash commands to register
const commands = [
  new SlashCommandBuilder()
    .setName('text')
    .setDescription('Repeats text 20x with header format')
    .addStringOption(option =>
      option.setName('input').setDescription('Text to repeat').setRequired(true)),
  new SlashCommandBuilder()
    .setName('textp')
    .setDescription('Same as /text but without credit footer')
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
    const isTextP = interaction.commandName === 'textp';

    if (isTextP && interaction.user.id !== ALLOWED_USER_ID) {
      return await interaction.reply({ content: 'You are not allowed to use this command.', ephemeral: true });
    }

    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder()
        .setCustomId(`confirm-${interaction.commandName}-${input}`)
        .setLabel('Yes')
        .setStyle(ButtonStyle.Primary)
    );

    await interaction.reply({
      content: 'Are you sure? Spam the button.',
      ephemeral: true,
      components: [row],
    });
  }

  if (interaction.isButton()) {
    const [prefix, cmd, input] = interaction.customId.split('-');
    if (!input) return;

    let content = `# ${input.toUpperCase()}\n`.repeat(20);
    if (cmd === 'text') {
      content += `\n**Made by** [YOUR SERVER INVITE LINK]`;
    }

    const embed = new EmbedBuilder()
      .setTitle('Message:')
      .setDescription(content);

    await interaction.reply({ embeds: [embed] });
  }
});

client.login(BOT_TOKEN);

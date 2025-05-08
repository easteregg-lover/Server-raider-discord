//Disclaimer bc some people donrt read Readme.md:
//I AM NOT RESPONSIBLE FOR ANY ISSUES, DAMAGES, OR CONSEQUENCES THAT MAY OCCUR FROM THE USE, COPYING, OR DISTRIBUTION OF THIS CODE. BY PROCEEDING, YOU AGREE TO THESE TERMS.

const { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

const BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE';
const CLIENT_ID = 'YOUR_BOT_CLIENT_ID_HERE';
const ALLOWED_USER_ID = 'SOMEONES_ID'; // Replace with the allowed user's ID

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

const commands = [
  new SlashCommandBuilder()
    .setName('embed')
    .setDescription('Repeats text 100x with header format (embed + credit footer)')
    .addStringOption(option =>
      option.setName('input').setDescription('Text to repeat').setRequired(true)),
  new SlashCommandBuilder()
    .setName('embedwithoutcredits')
    .setDescription('Same as embed but sends embed without credit footer')
    .addStringOption(option =>
      option.setName('input').setDescription('Text to repeat').setRequired(true)),
  new SlashCommandBuilder()
    .setName('normal')
    .setDescription('Same as embed but sends normal message (with credit footer)')
    .addStringOption(option =>
      option.setName('input').setDescription('Text to repeat').setRequired(true)),
  new SlashCommandBuilder()
    .setName('normalwithoutcredits')
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

    // Check if user is allowed to use restricted commands
    if ((commandName === 'embedwithoutcredits' || commandName === 'normalwithoutcredits') 
        && interaction.user.id !== ALLOWED_USER_ID) {
      return await interaction.reply({
        content: 'You are not authorized to use this command.',
        flags: 1 << 6, // Send ephemeral message
      });
    }

    // Multiply input by 100 and check character limit
    let content = `# ${input.toUpperCase()}\n`.repeat(100);
    if (content.length > 2000) {
      return await interaction.reply({
        content: 'Too long message! Remember your message is multiplied by 100!',
        flags: 1 << 6, // Send ephemeral message
      });
    }

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
        content += `\n**Made by** https://discord.gg/6WYaURhZCF`;
        const embedText = new EmbedBuilder()
          .setTitle('Message:')
          .setDescription(content);
        await interaction.reply({ embeds: [embedText] });
        break;
      case 'embedwithoutcredits':
        const embedWithoutCredits = new EmbedBuilder()
          .setTitle('Message:')
          .setDescription(content);
        await interaction.reply({ embeds: [embedWithoutCredits] });
        break;
      case 'normal':
        content += `\n**Made by** https://discord.gg/6WYaURhZCF`;
        await interaction.reply({ content });
        break;
      case 'normalwithoutcredits':
        await interaction.reply({ content });
        break;
    }
  }
});

client.login(BOT_TOKEN);

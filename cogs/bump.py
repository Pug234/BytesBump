import discord, io, traceback, json, os

from colorama import Fore, Style, init

init(autoreset=True)

from core.database import Servers
from core.files import Data
from core.embeds import Embeds

commands = discord.ext.commands

settings = Data("settings").json_read()

class Bumps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Data("config").yaml_read()

    @commands.guild_only()
    @commands.cooldown(1, settings['cooldown'], commands.BucketType.guild)
    @commands.command()
    async def bump(self, ctx):
        server = Servers(ctx.guild.id)
        
        if not server.get():
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(embed=Embeds(f"You must setup this server first! Use `{self.config['prefix']}setup` to do so!"))

        servers = Servers().get_all()

        success, fail = 0, 0

        for entry in servers:
            try:
                server = self.bot.get_guild(entry['_id'])
                webhook = await self.bot.fetch_webhook(entry['webhook'])
                invite_channel = self.bot.get_channel(entry['invite'])
                
                invite = await invite_channel.create_invite(max_uses=0, max_age=0, unique=False)

                embed = discord.Embed(
                    title=server.name,
                    description=entry['description'],
                    color=discord.Color(value=entry['color']),
                    url=invite.url
                )

                embed.add_field(name="🌍 Members", value=len(server.members))
                embed.add_field(name="🤣 Emojis", value=f"{len(server.emojis)}/{server.emoji_limit}")
                embed.add_field(name="💎 Boost Tier", value=f"Tier {server.premium_tier} ({server.premium_subscription_count} Boosts)")
                embed.add_field(name="👑 Owner", value=str(server.owner))
                embed.add_field(name="🔗 Invite", value=f"[Click to join!]({invite.url})")
                embed.set_thumbnail(url=server.icon_url_as(static_format="png"))
                embed.set_footer(text=f"Powered by • {self.config['bot_name']}")


                await webhook.send(
                    username=self.config['bot_name'],
                    avatar_url=self.bot.user.avatar_url,
                    embed=embed
                )

                success += 1
            except Exception as e:
                error = f"{e.__class__.__name__}"
                value = io.StringIO().getvalue()
                print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}{error}\n{Fore.YELLOW}Error was recorded in {Fore.RED}error.log")
                #with open("error.log", "w+") as f:
                    #f.write(f"{value}{traceback.format_exc()}")

                """
                with open("cache_data.json", "w+") as f:
                    json.dump(entry, f, indent=4)
                """
                Servers(entry['_id']).delete()

                try:
                    await self.bot.get_guild(entry['_id']).owner.send(embed=discord.Embed(
                        title="⚠️ Server Removed ⚠️",
                        description="Your server was removed from the database because it caused an error! Make sure I have permission to `Manage Webhooks` and `Create Instant Invites`! I've attached your server info below.",
                        color=discord.Color.red()
                    ))

                except: pass

                fail += 1

                #os.remove("cache_data.json")
        
        return await ctx.send(embed=discord.Embed(
            title="⏫ Server Bumped",
            description=f"Your server was bumped to `{success+fail}` servers!\n✅ There were `{success}` successful bumps!\n❎ There were `{fail}` failed ones, they got booted from the Database!",
            color=discord.Color.green()
        )
        .set_footer(text=f"Powered by • {self.config['bot_name']}"))

def setup(bot):
    bot.add_cog(Bumps(bot))
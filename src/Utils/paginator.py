import discord
from discord.ui import View, Button

class Paginator(View):
    def __init__(
        self,
        items: list[str],
        title: str = "Results",
        per_page: int = 10,
        color: discord.Color = discord.Color.blurple(),
        timeout: int = 120,
    ):
        super().__init__(timeout=timeout)
        self.items = items
        self.title = title
        self.per_page = per_page
        self.color = color
        self.page = 0
        self.total_pages = max(1, (len(items) + per_page - 1) // per_page)

        # Disable buttons if not needed
        self.prev_button.disabled = True
        if self.total_pages == 1:
            self.next_button.disabled = True

    def get_page_content(self) -> discord.Embed:
        """Return the current page as an Embed."""
        start = self.page * self.per_page
        end = start + self.per_page
        current_items = self.items[start:end]

        embed = discord.Embed(
            title=f"{self.title}",
            description="\n".join(current_items) or "*No items to display.*",
            color=self.color
        )
        embed.set_footer(text=f"Page {self.page + 1}/{self.total_pages} • {len(self.items)} total")
        return embed

    async def update(self, interaction: discord.Interaction):
        """Update the embed and buttons."""
        await interaction.response.edit_message(embed=self.get_page_content(), view=self)

    @discord.ui.button(label="⬅️ Prev", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
            self.next_button.disabled = False
            if self.page == 0:
                button.disabled = True
            await self.update(interaction)

    @discord.ui.button(label="Next ➡️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if self.page < self.total_pages - 1:
            self.page += 1
            self.prev_button.disabled = False
            if self.page == self.total_pages - 1:
                button.disabled = True
            await self.update(interaction)

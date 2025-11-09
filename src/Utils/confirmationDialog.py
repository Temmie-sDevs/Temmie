import discord
from discord.ui import View, button
from typing import Callable, Any

class ConfirmationView(View):
    """
    Generic confirmation view with Yes/No buttons.
    
    :param user: Only this user can respond.
    :param on_confirm: Async callback function when "Yes" is clicked.
                       It receives the interaction as argument.
    :param on_cancel: Optional async callback function when "No" is clicked.
    :param timeout: Seconds before the confirmation times out.
    """
    def __init__(
        self,
        user: discord.User,
        on_confirm: Callable[[discord.Interaction], Any],
        on_cancel: Callable[[discord.Interaction], Any] = None,
        timeout: int = 30
    ):
        super().__init__(timeout=timeout)
        self.user = user
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.result = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user.id

    @button(label="✅ Yes", style=discord.ButtonStyle.secondary)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.on_confirm:
            await self.on_confirm(interaction)
        self.result = True
        self.stop()

    @button(label="❌ No", style=discord.ButtonStyle.primary)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.on_cancel:
            await self.on_cancel(interaction)
        self.result = False
        self.stop()

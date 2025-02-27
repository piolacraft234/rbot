
@bot.tree.command(name='search', description='Busca un nick/ip')
async def find(interaction: discord.Interaction, nick: str):
    role_id_finder = 1289407040518754359
#   role_id_finder = 1289407081358823459
    role_id_decrypt = 1289407040518754359

    print(f"[BUSQUEDA REALIZADA] ID: {interaction.user.id} - - - {nick}")

    if any(role.id == role_id_finder for role in interaction.user.roles):
        if not 3 <= len(nick) <= 16:
            await interaction.response.send_message(f"{interaction.user.mention} Introduzca bien el nick/ip", ephemeral=True)
            return
        if nick.startswith("."):
            busqueda = "name"
        elif "." in nick:
            busqueda = "ip"
        else:
            busqueda = "name"

        # Enviar mensaje inicial
        embed = discord.Embed(title=f"<:palomita:1289455204349251606> Buscando informacion de {nick} ",
        color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)        
        start_time = time.time()
        search_results = await search_nick_in_api(nick)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if search_results:
            current_page = 0

            def verificar_usuario_premium(nick):
                mojang_api_url = f"https://api.mojang.com/users/profiles/minecraft/{nick}"
                response = requests.get(mojang_api_url)
                if response.status_code == 200:
                    return "<:palomita:1289455204349251606>"
                else:
                    return "<:cruz:1289455264746967070>"

            def generate_embed(page):
                entry = search_results[page]
                premium_status = verificar_usuario_premium(nick)
                icon_url = f"https://minotar.net/avatar/{entry.get('name', 'steve')}/65"
                image2 = f"http://status.mclive.eu/{entry.get('server', 'No encontrado')}/{entry.get('serverip', 'No encontrado')}/banner.png"
                image3 = f"https://eu.mc-api.net/v3/server/favicon/{entry.get('serverip', 'No encontrado')}"
                serverip = entry.get('serverip', 'NULL')

                embed = discord.Embed(title=f"**{entry.get('server', 'No encontrado')}**", color=discord.Color.green())
                embed.set_thumbnail(url=image3)
                embed.set_image(url=image2)
                embed.set_author(name=f"{entry.get('name', 'No encontrado')}", icon_url=icon_url)

                password_value = entry.get('password', 'No encontrado')
                if isinstance(password_value, bytes):
                    password_value = password_value.decode('utf-8', errors='replace')  # Decodifica en UTF-8
                try:
                    password_value = password_value.encode('latin1').decode('utf-8')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    password_value = "Error"
                password_value2 = entry.get('password')
                if password_value2 == "null":
                    password_value = "No encontrado"
                if len(password_value) > 31 and password_value != "No encontrado":
                    embed.add_field(name="<:password:1289455646407786559> **Hash**", value=f"```{password_value}```", inline=False)
                    
                else:
                    embed.add_field(name="<:password:1289454463517458513> **Password**", value=f"**```{password_value}```**", inline=False)

                salt_value = entry.get('salt', 'No encontrado')
                if salt_value != 'No encontrado' and len(password_value) > 31:
                    embed.add_field(name="<:salt:1289455739299037205> **Salt**", value=f"```{salt_value}```", inline=True)
                
                email = entry.get('email', 'No encontrado')
                if email != 'No encontrado':
                    embed.add_field(name=":e_mail: **Email**", value=f"```{email}```", inline=False)
                
                ip_value = entry.get('ip', 'No encontrado')
                if ip_value != 'No encontrado':
                    embed.add_field(name="<:ping:1289455399061295146> **IP**", value=f"```{ip_value}```", inline=True)

                embed.add_field(name=f":scroll: **Premium**: {premium_status}", value=f"", inline=False)
                embed.set_footer(text=f'>> {serverip} | Pagina: {page + 1}/{len(search_results)} |')
                return embed

            class PageView(discord.ui.View):
                def __init__(self, user_roles, password_length, compras_results=None):
                    super().__init__(timeout=None)

                    self.user_roles = user_roles
                    self.password_length = password_length
                    self.compras_results = compras_results
                    self.showing_compras = False

                    self.previous_page_button = discord.ui.Button(emoji='<:izquierda:1315817856889258024>', custom_id="back", style=discord.ButtonStyle.primary)
                    self.previous_page_button.callback = self.previous_page
                    self.add_item(self.previous_page_button)

                    self.decrypt_button = discord.ui.Button(label='Desencriptar', style=discord.ButtonStyle.danger)
                    self.decrypt_button.callback = self.decrypt_password
                    self.add_item(self.decrypt_button)

                    self.next_page_button = discord.ui.Button(emoji='<:derecha:1315817927315947550>', custom_id="next", style=discord.ButtonStyle.primary)
                    self.next_page_button.callback = self.next_page
                    self.add_item(self.next_page_button)

                    if self.compras_results:
                        self.show_compras_button = discord.ui.Button(label='Compras', style=discord.ButtonStyle.green)
                        self.show_compras_button.callback = self.show_compras
                        self.add_item(self.show_compras_button)

                        if not self.showing_compras:
                            self.show_passwords_button = discord.ui.Button(label='Passwords', style=discord.ButtonStyle.green)
                            self.show_passwords_button.callback = self.show_passwords
                            self.add_item(self.show_passwords_button)

                    self.update_button_states()

                def update_button_states(self):
                    self.previous_page_button.disabled = current_page == 0
                    self.next_page_button.disabled = current_page == (len(self.compras_results) - 1 if self.showing_compras else len(search_results) - 1)
                    self.decrypt_button.disabled = not (any(role.id == role_id_decrypt for role in self.user_roles) and self.password_length > 0 and not self.showing_compras)

                async def show_compras(self, interaction: discord.Interaction):
                    nonlocal current_page
                    self.showing_compras = True
                    current_page = 0
                    self.update_button_states()
                    await interaction.response.edit_message(embed=self.generate_compras_embed(current_page), view=self)

                async def show_passwords(self, interaction: discord.Interaction):
                    nonlocal current_page
                    self.showing_compras = False
                    current_page = 0
                    self.update_button_states()
                    await interaction.response.edit_message(embed=generate_embed(current_page), view=self)

                async def previous_page(self, interaction: discord.Interaction):
                    nonlocal current_page
                    if current_page > 0:
                        current_page -= 1
                        self.update_button_states()
                        await interaction.response.edit_message(embed=self.generate_compras_embed(current_page) if self.showing_compras else generate_embed(current_page), view=self)

                async def next_page(self, interaction: discord.Interaction):
                    await interaction.response.defer()

                    nonlocal current_page
                    if current_page < (len(self.compras_results) - 1 if self.showing_compras else len(search_results) - 1):
                        current_page += 1
                        self.update_button_states()
                        await interaction.edit_original_response(
                            embed=self.generate_compras_embed(current_page) if self.showing_compras else generate_embed(current_page),
                            view=self
                        )

                async def decrypt_password(self, interaction: discord.Interaction):
                        entry = search_results[current_page]
                        password = entry.get('password', 'No encontrado')

                        if len(password) > 31:
                            api_url = "http://localhost:34765/dehash"
                            headers = {"Content-Type": "application/json"}
        
        # Preparar el payload con hash, salt, server y name
                            data = {
                                "hash": password,
                                "server": entry.get('server', 'No encontrado'),  # Usar el nombre del servidor
                                "name": entry.get('name', 'No encontrado')       # Agregar el nombre
                            }
        
                            if entry.get('salt') != 'No encontrado':
                                data["salt"] = entry.get('salt')
                    
                            async with aiohttp.ClientSession() as session:
                                async with session.post(api_url, headers=headers, json=data) as response:
                                    if response.status == 200:
                                        decrypted_data = await response.json()
                                        decrypted_password = decrypted_data.get('password', 'No encontrado')
                                        if decrypted_password != 'No encontrado':
                                            entry['password'] = decrypted_password
                                            await interaction.response.edit_message(embed=generate_embed(current_page), view=self)
                                    else:
                                        entry['password'] += " (No se pudo dehashear)"
                                        await interaction.response.edit_message(embed=generate_embed(current_page), view=self)


                def generate_compras_embed(self, page):
                    entry = self.compras_results[page]
                    embed = discord.Embed(title="Compras del Usuario", color=discord.Color.blue())
                    embed.add_field(name="Fecha", value=entry.get('archivo', 'Desconocido'), inline=False)
                    embed.add_field(name="Usuario", value=entry.get('name', 'Desconocido'), inline=False)
                    embed.add_field(name="Paquete", value=entry.get('paquete', 'Desconocido'), inline=False)
                    embed.add_field(name="Servidor", value=entry.get('server', 'Desconocido'), inline=False)
                    embed.set_footer(text=f'Nordify Finder | Pagina: {page + 1}/{len(self.compras_results)} |')
                    return embed

            compras_results = await search_nick_in_compras_api(nick)
            if compras_results:
                print(f"Resultados de compras para {nick}: {compras_results}")
            else:
                print(f"No se encontraron compras para {nick}.")

            view = PageView(interaction.user.roles, len(search_results), compras_results)
            await interaction.edit_original_response(embed=generate_embed(current_page), view=view)
        else:
            embed = discord.Embed(title=f":x: No se encontraron resultados para {nick} :x:",
            color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(f"<:cruz:1289455264746967070> {interaction.user.mention} No tienes permisos para buscar un nick/ip", ephemeral=True)

@find.error
async def find_error(interaction, error) :
    if isinstance(error, commands.CommandOnCooldown) :
        await interaction.response.send_message(
            f"{interaction.user.mention} Espera {error.retry_after:.2f} segundos antes de usar este comando de nuevo")


ROLE_MAPPING = {
    'finder' : 1289407040518754359,
    'dehasher' : 1289407040518754359
}

class UpgradeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.URL, label="Upgrade", url="https://tu-enlace-aqui.com")

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(UpgradeButton())
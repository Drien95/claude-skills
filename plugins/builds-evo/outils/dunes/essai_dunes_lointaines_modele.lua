-- A2 « Le Sable du Fond » : dunes de fermeture en script. Planche 2 (26/11/2026). Client seulement.
-- Couches 2 et 3 (r ~1 060 et ~1 270, hauteurs ~105 et ~180 u, profils variés) en maillage lisse, et le même sable
-- drapé sur la couche 1 en props (8 demi-tubes) : pied adouci qui se fond dans le sol, bouts des tubes recouverts.
-- Mêmes matériau, teintes et éclairage par sommet que la surface du sol v4 (essai_surface_sable.lua) ; fondu au noir
-- avec la distance. Hauteurs calculées par build_p2.py (DONNEES plus bas, générées : ne pas éditer à la main).
-- Tout est relatif au prop de tête du dupe (pan du fond, plate5x5 teinte 75,70,64) : aucune coordonnée de map.
-- Console (aucune touche en dur) :
--   a2_dunes <0|1>   éteint / allumé

local MODELE_TETE = "models/hunter/plates/plate5x5.mdl"
local TEINTE_TETE = { 75, 70, 64 }
local TETE = Vector(-226, -226, -61.5)
local Z0 = -0.83 + 2.5 + 0.4          -- dessus du sable du sol extérieur (v4) + 0,4 u : pas de scintillement au raccord
local MAT = "nature/dirtfloor_mine001a"
local ECHELLE, ECHELLE_DETAIL = 512, 128
local VOILE = { 85, 82, 78 }
local ALPHA_VOILE, ALPHA_DETAIL = 0.5, 0.4
local RELIEF = 2.2
local PAR_SECTEUR = 64                -- segments d'angle par maillage (taille de maillage bornée)

local DONNEES = nil --[[DONNEES]]

local etat = { allume = true }
local mats = nil
local tete, prochaineRecherche = nil, 0
local meshes, cle = nil, nil

local function creer(nom, suffixe, params)
	local m = CreateMaterial("a2_dunes2_" .. string.gsub(nom, "%W", "_") .. suffixe, "UnlitGeneric", params)
	local tex = m:GetTexture("$basetexture")
	if m:IsError() or not tex or tex:IsError() then return nil end
	return m
end
local function materiaux()
	if mats ~= nil then return mats end
	local base = creer(MAT, "", { ["$basetexture"] = MAT, ["$vertexcolor"] = 1, ["$nocull"] = 1 })
	local detail = creer(MAT, "_d", { ["$basetexture"] = MAT, ["$vertexcolor"] = 1, ["$vertexalpha"] = 1, ["$translucent"] = 1, ["$nocull"] = 1 })
	local voile = creer("vgui/white", "_v", { ["$basetexture"] = "vgui/white", ["$vertexcolor"] = 1, ["$vertexalpha"] = 1, ["$translucent"] = 1, ["$nocull"] = 1 })
	if not (base and detail and voile) then
		print("[a2_dunes] texture absente : " .. MAT)
		mats = false
		return false
	end
	mats = { base = base, detail = detail, voile = voile }
	return mats
end

local function memeTeinte(e)
	local c = e:GetColor()
	return math.abs(c.r - TEINTE_TETE[1]) <= 1 and math.abs(c.g - TEINTE_TETE[2]) <= 1 and math.abs(c.b - TEINTE_TETE[3]) <= 1
end
local function chercherTete()
	local meilleur, score = nil, math.huge
	for _, e in ipairs(ents.FindByModel(MODELE_TETE)) do
		if IsValid(e) and memeTeinte(e) then
			local p = e:GetPos()
			if p.x + p.y < score then meilleur, score = e, p.x + p.y end
		end
	end
	return meilleur
end
local function versMonde(x, y, z) return tete:LocalToWorld(Vector(x, y, z) - TETE) end
local function lisse(a, b, t) t = math.Clamp((t - a) / (b - a), 0, 1) return t * t * (3 - 2 * t) end
local function soleil()
	local info = util.GetSunInfo and util.GetSunInfo()
	local d = info and info.direction
	if not d or d.z < 0.2 then d = Vector(-0.45, 0.35, 0.82) end
	return d:GetNormalized()
end

-- lecture des hauteurs (une chaîne par anneau, nombres séparés par des espaces)
local function lire(v)
	local Z = {}
	for i, ligne in ipairs(v.z) do
		local t, j = {}, 0
		for n in string.gmatch(ligne, "%S+") do t[j] = tonumber(n) j = j + 1 end
		assert(j == DONNEES.seg, "[a2_dunes] anneau " .. i .. " : " .. j .. " valeurs")
		Z[i] = t
	end
	return Z
end

local function grille(v)
	local R, SEG = DONNEES.anneaux, DONNEES.seg
	local Z = lire(v)
	local sun = soleil()
	local da = math.pi * 2 / SEG
	local G = {}
	for i, r in ipairs(R) do
		local ligne = {}
		for j = 0, SEG - 1 do
			local a = j * da
			local z = Z[i][j]
			local i0, i1 = math.max(i - 1, 1), math.min(i + 1, #R)
			local dzr = (Z[i1][j] - Z[i0][j]) / math.max(R[i1] - R[i0], 1)
			local dzt = (Z[i][(j + 1) % SEG] - Z[i][(j - 1) % SEG]) / (2 * r * da)
			local ca, sa = math.cos(a), math.sin(a)
			local n = Vector(-(dzr * ca - dzt * sa), -(dzr * sa + dzt * ca), 1):GetNormalized()
			local lum = math.Clamp(1 + RELIEF * (n:Dot(sun) / sun.z - 1), 0.4, 1.4)
			local F = DONNEES.fondu or { 1350, 1750 }
			local fondu = 1 - 0.97 * lisse(F[1], F[2], r)
			ligne[j] = { x = v.ox + ca * r, y = sa * r, z = Z0 + z, k = lum * fondu }
		end
		G[i] = ligne
	end
	return G
end

local function passe(G, j0, j1, dz, echelle, rot, couleur, alpha)
	local SEG = DONNEES.seg
	local m = Mesh()
	local cr, sr = math.cos(rot), math.sin(rot)
	mesh.Begin(m, MATERIAL_QUADS, (#G - 1) * (j1 - j0))
	for i = 1, #G - 1 do
		local A, B = G[i], G[i + 1]
		for j = j0, j1 - 1 do
			local j2 = (j + 1) % SEG
			for _, s in ipairs({ A[j], B[j], B[j2], A[j2] }) do
				mesh.Position(versMonde(s.x, s.y, s.z + dz))
				mesh.TexCoord(0, (s.x * cr - s.y * sr) / echelle, (s.x * sr + s.y * cr) / echelle)
				mesh.Color(math.min(255, couleur[1] * s.k), math.min(255, couleur[2] * s.k), math.min(255, couleur[3] * s.k), alpha)
				mesh.AdvanceVertex()
			end
		end
	end
	mesh.End()
	return m
end

local function construire()
	for _, l in pairs(meshes or {}) do for _, m in ipairs(l) do m:Destroy() end end
	meshes = { base = {}, detail = {}, voile = {} }
	local blanc = { 225, 222, 216 }
	local voile = { VOILE[1] * 1.15, VOILE[2] * 1.15, VOILE[3] * 1.15 }
	for _, v in ipairs(DONNEES.variantes) do
		local G = grille(v)
		for j0 = 0, DONNEES.seg - 1, PAR_SECTEUR do
			local j1 = math.min(j0 + PAR_SECTEUR, DONNEES.seg)
			table.insert(meshes.base, passe(G, j0, j1, 0, ECHELLE, 0, blanc, 255))
			table.insert(meshes.detail, passe(G, j0, j1, 0.08, ECHELLE_DETAIL, 0.41, blanc, 255 * ALPHA_DETAIL))
			table.insert(meshes.voile, passe(G, j0, j1, 0.16, ECHELLE, 0, voile, 255 * ALPHA_VOILE))
		end
	end
end

hook.Add("PostDrawOpaqueRenderables", "a2_dunes_lointaines", function(prof, ciel)
	if prof or ciel or not etat.allume or not DONNEES then return end
	if CurTime() >= prochaineRecherche then
		prochaineRecherche = CurTime() + 1
		tete = chercherTete()
	end
	if not IsValid(tete) then return end
	local M = materiaux()
	if not M then return end
	local nouvelle = tostring(tete:GetPos()) .. tostring(tete:GetAngles())
	if nouvelle ~= cle or not meshes then cle = nouvelle; construire() end
	render.SetMaterial(M.base); for _, m in ipairs(meshes.base) do m:Draw() end
	render.SetMaterial(M.detail); for _, m in ipairs(meshes.detail) do m:Draw() end
	render.SetMaterial(M.voile); for _, m in ipairs(meshes.voile) do m:Draw() end
end)

concommand.Add("a2_dunes", function(_, _, args)
	etat.allume = tonumber(args[1] or "") == 1
	print("[a2_dunes] " .. (etat.allume and "allumé" or "éteint"))
end)

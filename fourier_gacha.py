# SPDX-License-Identifier: GPL-3.0-or-later
bl_info = {
    "name": "Fourier Gacha",
    "author": "textout",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Gacha",
    "description": "2重フーリエ展開で、ランダムな有機的形状を次々に生成する (Blender 3.6 LTS)",
    "category": "Add Mesh",
}

import bpy
import numpy as np

MAXLV = 64                 # 形状レベルの上限(係数はここまで全部保存する)
OBJ_NAME = "FourierShape"
_topo_cache = {}


# ---------------- 多言語化 ----------------
# 英語の原文をキーにして、各言語へ翻訳する。
# "Subdivisions" はBlender内蔵辞書で「細分化」等に当たってしまうため、
# 内蔵辞書と衝突しにくい "Division Count" をキーにしている。
_MSG_TOOLTIP = "Generate a new shape"
_MSG_WARN = "Please run in Object Mode"
_MSG_DIV = "Division Count"
_MSG_LEVEL = "Shape Level"

# 順序: (ツールチップ, 警告メッセージ, 分割数, 形状レベル)
_TR = {
    "ja_JP": ("新しい形状を生成する", "オブジェクトモードで実行してください", "分割数", "形状レベル"),
    "zh_CN": ("生成新的形状", "请在物体模式下运行", "细分数", "形状级别"),
    "zh_TW": ("產生新的形狀", "請在物件模式下執行", "細分數", "形狀等級"),
    "ko_KR": ("새로운 형상 생성", "오브젝트 모드에서 실행해 주세요", "분할 수", "형상 레벨"),
    "fr_FR": ("Générer une nouvelle forme", "Veuillez exécuter en mode Objet", "Subdivisions", "Niveau de forme"),
    "de_DE": ("Neue Form erzeugen", "Bitte im Objektmodus ausführen", "Unterteilungen", "Formstufe"),
    "es": ("Generar una nueva forma", "Ejecute en modo Objeto", "Subdivisiones", "Nivel de forma"),
    "es_ES": ("Generar una nueva forma", "Ejecute en modo Objeto", "Subdivisiones", "Nivel de forma"),
    "ru_RU": ("Создать новую форму", "Выполните в объектном режиме", "Число разбиений", "Уровень формы"),
    "pt_BR": ("Gerar uma nova forma", "Execute no Modo de Objeto", "Subdivisões", "Nível da forma"),
    "pt_PT": ("Gerar uma nova forma", "Execute no Modo de Objeto", "Subdivisões", "Nível da forma"),
    "it_IT": ("Genera una nuova forma", "Eseguire in modalità Oggetto", "Suddivisioni", "Livello della forma"),
    "ar_EG": ("إنشاء شكل جديد", "يرجى التشغيل في وضع الكائن", "عدد التقسيمات", "مستوى الشكل"),
    "bg_BG": ("Генериране на нова форма", "Моля, изпълнете в обектен режим", "Брой подразделения", "Ниво на формата"),
    "ca_AD": ("Genera una forma nova", "Executeu-ho en mode Objecte", "Subdivisions", "Nivell de forma"),
    "cs_CZ": ("Vytvořit nový tvar", "Spusťte v objektovém režimu", "Počet dělení", "Úroveň tvaru"),
    "el_GR": ("Δημιουργία νέου σχήματος", "Εκτελέστε σε λειτουργία αντικειμένου", "Υποδιαιρέσεις", "Επίπεδο σχήματος"),
    "eu_EU": ("Sortu forma berri bat", "Exekutatu Objektu moduan", "Zatiketak", "Forma-maila"),
    "fa_IR": ("ایجاد شکل جدید", "لطفاً در حالت شیء اجرا کنید", "تعداد تقسیمات", "سطح شکل"),
    "fi_FI": ("Luo uusi muoto", "Suorita objektitilassa", "Jakojen määrä", "Muototaso"),
    "ha_NG": ("Ƙirƙiri sabon siffa", "Da fatan za a gudanar a yanayin Object", "Adadin rarrabawa", "Matakin siffa"),
    "he_IL": ("צור צורה חדשה", "אנא הפעל במצב אובייקט", "מספר חלוקות", "רמת צורה"),
    "hi_IN": ("नया आकार बनाएँ", "कृपया ऑब्जेक्ट मोड में चलाएँ", "विभाजन संख्या", "आकार स्तर"),
    "hr_HR": ("Generiraj novi oblik", "Pokrenite u objektnom načinu", "Broj podjela", "Razina oblika"),
    "hu_HU": ("Új alakzat létrehozása", "Futtassa objektum módban", "Felosztások száma", "Alakzatszint"),
    "id_ID": ("Buat bentuk baru", "Jalankan dalam Mode Objek", "Jumlah subdivisi", "Level bentuk"),
    "km_KH": ("បង្កើតរូបរាងថ្មី", "សូមដំណើរការក្នុងរបៀបវត្ថុ", "ចំនួនការបែងចែក", "កម្រិតរូបរាង"),
    "ky_KG": ("Жаңы форма түзүү", "Объект режиминде иштетиңиз", "Бөлүүлөрдүн саны", "Форма деңгээли"),
    "ne_NP": ("नयाँ आकार बनाउनुहोस्", "कृपया अब्जेक्ट मोडमा चलाउनुहोस्", "विभाजन संख्या", "आकार स्तर"),
    "nl_NL": ("Nieuwe vorm genereren", "Voer uit in Objectmodus", "Onderverdelingen", "Vormniveau"),
    "pl_PL": ("Wygeneruj nowy kształt", "Uruchom w trybie obiektowym", "Liczba podziałów", "Poziom kształtu"),
    "ro_RO": ("Generează o formă nouă", "Rulați în modul Obiect", "Număr de diviziuni", "Nivel formă"),
    "sk_SK": ("Vytvoriť nový tvar", "Spustite v objektovom režime", "Počet delení", "Úroveň tvaru"),
    "sl_SI": ("Ustvari novo obliko", "Zaženite v objektnem načinu", "Število delitev", "Raven oblike"),
    "sr_RS": ("Генериши нови облик", "Покрените у објектном режиму", "Број подела", "Ниво облика"),
    "sr_RS@latin": ("Generiši novi oblik", "Pokrenite u objektnom režimu", "Broj podela", "Nivo oblika"),
    "sv_SE": ("Generera en ny form", "Kör i objektläge", "Antal indelningar", "Formnivå"),
    "ta_IN": ("புதிய வடிவத்தை உருவாக்கு", "பொருள் பயன்முறையில் இயக்கவும்", "பிரிவுகளின் எண்ணிக்கை", "வடிவ நிலை"),
    "th_TH": ("สร้างรูปร่างใหม่", "โปรดรันในโหมดวัตถุ", "จำนวนการแบ่ง", "ระดับรูปร่าง"),
    "tr_TR": ("Yeni bir şekil oluştur", "Nesne Modunda çalıştırın", "Bölüm sayısı", "Şekil seviyesi"),
    "uk_UA": ("Створити нову форму", "Запустіть в об'єктному режимі", "Кількість поділів", "Рівень форми"),
    "vi_VN": ("Tạo hình dạng mới", "Vui lòng chạy ở chế độ Object", "Số lần chia", "Cấp độ hình dạng"),
}

translations_dict = {
    loc: {
        ("*", _MSG_TOOLTIP): t[0],
        ("*", _MSG_WARN): t[1],
        ("*", _MSG_DIV): t[2],
        ("*", _MSG_LEVEL): t[3],
    }
    for loc, t in _TR.items()
}


# ---------------- 係数 ----------------
def random_full_coeffs():
    """r*p <= MAXLV の全係数を (2*random-1)/(r*p) で作る。A,B,C を連結して返す。"""
    rng = np.random.default_rng()
    r = np.arange(1, MAXLV + 1)
    rp = np.outer(r, r)
    mask = rp <= MAXLV

    def one():
        return np.where(mask, (2 * rng.random((MAXLV, MAXLV)) - 1) / rp, 0.0)

    return np.concatenate([one().ravel(), one().ravel(), one().ravel()])


def masked_coeffs(flat, level):
    """形状レベル level 以下 (r*p <= level) の係数だけを残す。"""
    M = MAXLV
    r = np.arange(1, level + 1)
    mask = np.outer(r, r) <= level
    A = flat[:M * M].reshape(M, M)[:level, :level] * mask
    B = flat[M * M:2 * M * M].reshape(M, M)[:level, :level] * mask
    C = flat[2 * M * M:].reshape(M, M)[:level, :level] * mask
    return A, B, C


# ---------------- 頂点 ----------------
def build_points(n, A, B, C):
    """経度緯度メッシュの頂点(北極, 南極, 各リング)。行列積でまとめて計算。"""
    L = A.shape[0]
    phi = np.arange(2 * n + 1) * np.pi / n
    th = np.arange(n + 1) * np.pi / n
    k = np.arange(1, L + 1)
    SP = np.sin(np.outer(phi, k))
    CP = np.cos(np.outer(phi, k))
    ST = np.sin(np.outer(th, k))
    x = (SP @ A.T) @ ST.T
    z = (CP @ C.T) @ ST.T
    y = np.cos(th)[None, :] + (CP @ B.T) @ ST.T

    X = np.empty(2 + (n - 1) * 2 * n); Y = X.copy(); Z = X.copy()
    X[0], Y[0], Z[0] = 0, 1, 0                  # 北極
    X[1], Y[1], Z[1] = 0, -1, 0                 # 南極
    X[2:] = x[:2 * n, 1:n].T.ravel()
    Y[2:] = y[:2 * n, 1:n].T.ravel()
    Z[2:] = z[:2 * n, 1:n].T.ravel()
    return np.stack([X, -Z, Y], axis=1)         # モデルのY軸(極)をBlenderのZ軸へ(回転)


# ---------------- 位相 ----------------
def build_topology(n):
    """面を (loops, starts, lens) の配列で返す。分割数ごとにキャッシュ。"""
    if n in _topo_cache:
        return _topo_cache[n]
    two = 2 * n

    def v(i, j):                                # 1 <= j <= n-1 のリング上の頂点番号
        return 2 + (j - 1) * two + (i % two)

    i = np.arange(two)
    north = np.stack([np.zeros(two, dtype=np.int64), v(i, 1), v(i + 1, 1)], 1)
    south = np.stack([v(i, n - 1), np.ones(two, dtype=np.int64), v(i + 1, n - 1)], 1)
    jj, ii = np.meshgrid(np.arange(1, n - 1), i, indexing='ij')
    quads = np.stack([v(ii, jj), v(ii, jj + 1), v(ii + 1, jj + 1), v(ii + 1, jj)],
                     -1).reshape(-1, 4)
    loops = np.concatenate([north.ravel(), quads.ravel(), south.ravel()]).astype(np.int32)
    lens = np.concatenate([np.full(len(north), 3), np.full(len(quads), 4),
                           np.full(len(south), 3)]).astype(np.int32)
    starts = (np.cumsum(lens) - lens).astype(np.int32)
    _topo_cache[n] = (loops, starts, lens)
    return _topo_cache[n]


def apply_topology(mesh, n, co):
    """同じメッシュデータの中身を、分割数 n の位相に差し替える。"""
    loops, starts, lens = build_topology(n)
    mesh.clear_geometry()
    mesh.vertices.add(len(co))
    mesh.vertices.foreach_set("co", co.ravel())
    mesh.loops.add(len(loops))
    mesh.loops.foreach_set("vertex_index", loops)
    mesh.polygons.add(len(lens))
    mesh.polygons.foreach_set("loop_start", starts)
    mesh.polygons.foreach_set("loop_total", lens)
    mesh.polygons.foreach_set("use_smooth", np.ones(len(lens), dtype=bool))
    mesh.update(calc_edges=True)
    mesh["fourier_n"] = n


# ---------------- 反映 ----------------
def find_obj(scene):
    for o in scene.objects:
        if o.type == 'MESH' and o.get("fourier_shape"):
            return o
    return None


def refresh(scene):
    """保存済みの係数と2つのスライダーの値から、形状を更新する。"""
    obj = find_obj(scene)
    if obj is None or obj.mode != 'OBJECT':
        return
    coef = obj.get("fourier_coef")
    if coef is None:
        return
    n = 2 ** scene.fourier_div
    level = scene.fourier_level
    A, B, C = masked_coeffs(np.array(coef.to_list(), dtype=float), level)
    co = build_points(n, A, B, C).astype(np.float32)

    mesh = obj.data
    if mesh.get("fourier_n") == n and len(mesh.vertices) == len(co):
        mesh.vertices.foreach_set("co", co.ravel())   # 位相は同じ: 頂点だけ更新
        mesh.update()
    else:
        apply_topology(mesh, n, co)                   # 分割数が変わった: 位相を差し替え


def _on_change(self, context):                        # self は Scene
    refresh(self)


# ---------------- UI ----------------
class FOURIER_OT_shuffle(bpy.types.Operator):
    bl_idname = "fourier.shuffle"
    bl_label = "Gacha!"
    bl_description = _MSG_TOOLTIP

    def execute(self, context):
        if context.mode != 'OBJECT':
            self.report({'WARNING'}, bpy.app.translations.pgettext_iface(_MSG_WARN))
            return {'CANCELLED'}
        sc = context.scene
        obj = find_obj(sc)
        if obj is None:
            mesh = bpy.data.meshes.new(OBJ_NAME)
            obj = bpy.data.objects.new(OBJ_NAME, mesh)
            obj["fourier_shape"] = True
            context.collection.objects.link(obj)
            context.view_layer.objects.active = obj
            obj.select_set(True)
        obj["fourier_coef"] = random_full_coeffs().tolist()
        refresh(sc)
        return {'FINISHED'}


class FOURIER_PT_panel(bpy.types.Panel):
    bl_label = "Fourier Gacha"
    bl_idname = "FOURIER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Gacha"

    def draw(self, context):
        sc = context.scene
        layout = self.layout
        layout.prop(sc, "fourier_div", slider=True)      # 上段
        layout.prop(sc, "fourier_level", slider=True)    # 中段
        layout.operator(FOURIER_OT_shuffle.bl_idname, text="Gacha!")  # 下段


def register():
    bpy.app.translations.register(__name__, translations_dict)
    bpy.types.Scene.fourier_div = bpy.props.IntProperty(
        name=_MSG_DIV, default=5, min=2, max=8, update=_on_change,
        description="")
    bpy.types.Scene.fourier_level = bpy.props.IntProperty(
        name=_MSG_LEVEL, default=12, min=1, max=MAXLV, update=_on_change)
    bpy.utils.register_class(FOURIER_OT_shuffle)
    bpy.utils.register_class(FOURIER_PT_panel)


def unregister():
    bpy.utils.unregister_class(FOURIER_PT_panel)
    bpy.utils.unregister_class(FOURIER_OT_shuffle)
    del bpy.types.Scene.fourier_level
    del bpy.types.Scene.fourier_div
    bpy.app.translations.unregister(__name__)


if __name__ == "__main__":
    register()

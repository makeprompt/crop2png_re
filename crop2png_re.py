import os
from tkinter import Tk, Canvas, Frame, Button, Toplevel, Entry, Label, filedialog, OptionMenu, StringVar
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES
import re
import csv

class ImageCropperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")

        self.canvas = Canvas(root, bg="gray")
        self.canvas.pack(expand=True, fill="both")

        self.image = None
        self.tk_image = None
        self.red_frame = None
        self.frame_start_x = 0
        self.frame_start_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.crop_coords = None
        self.display_scale = 1.0  # 表示倍率
        self.image_width = 0
        self.image_height = 0

        # 赤枠のデフォルトサイズ（元画像の座標系で指定）
        self.frame_width = 1024
        self.frame_height = 1024

        # プリセット定義(csv形式で取り込みに変更)
        # self.presets = [
        #     ['正1024 X 1024(1:1)',[1024,1024]],
        #     ['横1152 X  896(およそ4:3)',[1152,896]],
        #     ['横1216 X  832(およそ3:2)',[1216,832]],
        #     ['横1344 X  768(およそ16:9)',[1344,768]],
        #     ['横1568 X  672(21:9)',[1568,672]],
        #     ['横1728 X  576(3:1)',[1728,576]],
        #     ['縦 512 X 2048(1:4)',[512,2048]],
        #     ['縦 576 X 1728(1:3)',[576,1728]],
        #     ['縦 768 X 1344(およそ9:16)',[768,1344]],
        #     ['縦 832 X 1216(およそ2:3)',[832,1216]],
        #     ['縦 896 X 1152(3:4)',[896,1152]]
        # ]
        self.presets =[]
        try:
            with open(os.path.join(os.getcwd(),'presets.csv'), mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)  # ヘッダー行を自動認識
                for row in reader:
                    pname = row['pname']
                    width = int(row['width'])
                    height = int(row['height'])
                    self.presets.append([pname, [width, height]])
        except FileNotFoundError:
            print(f"エラー: ファイル presets.csv が見つかりません。")
        except KeyError as e:
            print(f"エラー: CSVファイルに欠けている列があります: {e}")
        except ValueError:
            print("エラー: 数値変換に失敗しました。CSVのフォーマットを確認してください。")
        # UI elements
        self.control_frame = Frame(root)
        self.control_frame.pack()
        # 恐らくドラッグアンドドロップ以外で始める人少ないと思うので通知欄に変更
        # Button(self.control_frame, text="Open Folder", command=self.load_folder).pack(side="left")
        self.label = Label(root, text="画像またはフォルダをドラッグ＆ドロップしてください")
        self.label.pack()
        self.image_files = []
        self.current_image_index = 0

        # キーボードイベントのバインド
        self.root.bind("s", lambda event: self.save_crop())
        self.root.bind("a", lambda event: self.save_image())
        # ドラッグ＆ドロップの設定
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)

        # サイズ変更ウィンドウを起動時に表示
        self.resize_window = self.create_resize_window()

    def on_drop(self, event):
        # ドラッグ＆ドロップされたファイルorフォルダを読み込む
        # Windows形式で追加される{}を削除してリスト化

        file_path = self.parse_file_paths(event.data)

        # print(file_path) #デバックprint

        # if file_path.startswith("{") and file_path.endswith("}"):
        #     file_path = re.findall(r'\{(.*?)\}',file_path)  # 非貪欲マッチ（最小マッチ）
        #     file_path.sort()
        # 複数ファイルがドラッグされた場合、ソートして最初の1つだけを処理
        if os.path.isfile(file_path[0]):
            self.load_dropped_file(file_path[0])
        
        if os.path.isdir(file_path[0]):
            self.load_dropped_folder(file_path[0])

    def parse_file_paths(self,data):

        # パスが{}で囲まれている場合を考慮
        pattern = r'(?<!\\)\"(.*?)\"|(?<!\\)\{(.*?)\}|(\S+)'  # ダブルクオート、波括弧、スペース区切り対応
        matches = re.findall(pattern, data)
        # マッチしたグループから値を抽出してリスト化
        return [match[0] or match[1] or match[2] for match in matches]

    def load_dropped_file(self, file_path):

        if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")):
            # 現在のフォルダパスを保存
            self.folder_path = os.path.dirname(file_path)

            # フォルダ内の画像ファイルをリスト化
            self.image_files = [
                f for f in os.listdir(self.folder_path)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"))
            ]
            self.image_files.sort()  # ファイル名でソート
            self.current_image_index = self.image_files.index(os.path.basename(file_path))

            self.load_image(os.path.join(self.folder_path, self.image_files[self.current_image_index]))

            # マウスホイールイベントをバインド
            self.root.bind("<MouseWheel>", self.scroll_image)

    def load_dropped_folder(self, file_path):
        # 現在のフォルダパスを保存
        self.folder_path = file_path

        # フォルダ内の画像ファイルをリスト化
        self.image_files = [
            f for f in os.listdir(self.folder_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"))
        ]
        self.image_files.sort()  # ファイル名でソート
        # 0枚目を開く
        self.load_image(os.path.join(self.folder_path, self.image_files[0]))

        # マウスホイールイベントをバインド
        self.root.bind("<MouseWheel>", self.scroll_image)

    def scroll_image(self, event):
        # マウスホイールで前後の画像に移動
        if self.image_files:
            if event.delta > 0:  # ホイールを上に動かした場合
                self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
            elif event.delta < 0:  # ホイールを下に動かした場合
                self.current_image_index = (self.current_image_index + 1) % len(self.image_files)

            # 新しい画像をロード
            new_image_path = os.path.join(self.folder_path, self.image_files[self.current_image_index])
            self.load_image(new_image_path)

    # 今は使用していないのでいずれ削除
    def load_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_files = [
                os.path.join(folder, file) for file in os.listdir(folder)
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
            ]
            if self.image_files:
                self.current_image_index = 0
                self.load_image(self.image_files[self.current_image_index])

    def load_image(self, image_path):
        self.image = Image.open(image_path)

        # 表示倍率を計算
        self.image_width, self.image_height = self.image.size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        scale_w = canvas_width / self.image_width
        scale_h = canvas_height / self.image_height
        self.display_scale = min(scale_w, scale_h)

        display_width = int(self.image_width * self.display_scale)
        display_height = int(self.image_height * self.display_scale)

        resized_image = self.image.resize((display_width, display_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        # 赤枠のサイズをスケールに合わせて調整
        scaled_width = self.frame_width * self.display_scale
        scaled_height = self.frame_height * self.display_scale

        # Draw red frame
        self.red_frame = self.canvas.create_rectangle(
            50, 50, 50 + scaled_width, 50 + scaled_height, outline="red", width=2
        )

        # Bind events
        self.bind_events()

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_click(self, event):
        # 赤枠の座標を取得
        x1, y1, x2, y2 = self.canvas.coords(self.red_frame)
        # クリック位置が赤枠内か確認
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            self.offset_x = event.x
            self.offset_y = event.y
        else:
            self.offset_x = None
            self.offset_y = None

    def on_drag(self, event):
        if self.offset_x is not None and self.offset_y is not None:
            dx = event.x - self.offset_x
            dy = event.y - self.offset_y

            # 移動後の新しい位置を計算
            x1, y1, x2, y2 = self.canvas.coords(self.red_frame)
            new_x1 = max(0, min(x1 + dx, self.image_width * self.display_scale - self.frame_width * self.display_scale))
            new_y1 = max(0, min(y1 + dy, self.image_height * self.display_scale - self.frame_height * self.display_scale))

            # 移動量を補正して赤枠を移動
            self.canvas.move(self.red_frame, new_x1 - x1, new_y1 - y1)

            # 更新
            self.offset_x = event.x
            self.offset_y = event.y
            # 画像の(0,0)を超えて移動しないことを確認

    def on_release(self, event):
        # ドラッグ終了時の赤枠の左上座標を取得
        if self.red_frame:
            x1, y1, _, _ = self.canvas.coords(self.red_frame)
            # キャンバス座標から元画像の座標に変換
            # original_x = x1 / self.display_scale
            # original_y = y1 / self.display_scale
            # 元画像での座標に変換する際、小数点以下を切り捨てる
            # キャンバス座標から元画像の座標に変換
            original_x = int( x1 / self.display_scale)
            original_y = int( y1 / self.display_scale)          
            # print(f"Red frame top-left position on original image: ({original_x:.2f}, {original_y:.2f})")
            # ドラッグ終了で仮に切り取る場合の範囲を設定
            # 現在の赤枠の設定値を取得して左上の元座標と合算して範囲を設定
            new_width = int(self.width_entry.get())
            new_height = int(self.height_entry.get())
            # 選択範囲を元の画像座標系に変換
            self.crop_coords = (
                original_x,
                original_y,
                original_x+new_width,
                original_y+new_height,
            )            


    def save_crop(self):
        if self.crop_coords and self.image:
            # 座標を取得してトリミング範囲を確定(範囲が画像サイズを超えた場合は画像サイズを最大とする)
            img_width, img_height = self.image.size            
            x1, y1, x2, y2 = map(int, self.crop_coords)
            x1, y1 = max(0, min(x1, img_width)), max(0, min(y1, img_height))
            x2, y2 = max(0, min(x2, img_width)), max(0, min(y2, img_height))

            # end_cropで順序はソートされているが念のため、再度範囲指定
            cropped_image = self.image.crop((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))) 


            # 保存フォルダの作成
            output_folder = os.path.join(os.getcwd(), "output")
            os.makedirs(output_folder, exist_ok=True)

            # 重複しないファイル名を生成(4桁0フィルで重複しない数値までチェックして保存)
            base_name = "crop"
            ext = ".png"
            counter = 1
            save_path = os.path.join(output_folder, f"{base_name}_{counter:04d}{ext}")
            while os.path.exists(save_path):
                counter += 1
                save_path = os.path.join(output_folder, f"{base_name}_{counter:04d}{ext}")

            # 画像を保存
            cropped_image.save(save_path)
            self.label.config(text=f"トリミングした画像を保存しました: {save_path}")
    def save_image(self):
        if self.image:

            # 保存フォルダの作成
            output_folder = os.path.join(os.getcwd(), "output")
            os.makedirs(output_folder, exist_ok=True)

            # 重複しないファイル名を生成(4桁0フィルで重複しない数値までチェックして保存)
            base_name = "crop"
            ext = ".png"
            counter = 1
            save_path = os.path.join(output_folder, f"{base_name}_{counter:04d}{ext}")
            while os.path.exists(save_path):
                counter += 1
                save_path = os.path.join(output_folder, f"{base_name}_{counter:04d}{ext}")

            # 画像を保存
            self.image.save(save_path)
            self.label.config(text=f"トリミングした画像を保存しました: {save_path}")

    def create_resize_window(self):
        resize_window = Toplevel(self.root)
        resize_window.title("Resize Red Frame")

        Label(resize_window, text="横幅 (px):").grid(row=0, column=0, padx=10, pady=5)
        width_entry = Entry(resize_window)
        width_entry.grid(row=0, column=1, padx=10, pady=5)
        width_entry.insert(0, str(self.frame_width))

        Label(resize_window, text="縦幅 (px):").grid(row=1, column=0, padx=10, pady=5)
        height_entry = Entry(resize_window)
        height_entry.grid(row=1, column=1, padx=10, pady=5)
        height_entry.insert(0, str(self.frame_height))

        def preset_choice(*args):
            # print(args)
            selected_value = preset_var.get()
            # print(selected_value)
            selected_value2 = dict(self.presets)[selected_value]
            # print(selected_value2)
            width_entry.delete(0,self.frame_width)
            width_entry.insert(0,selected_value2[0])
            height_entry.delete(0,self.frame_height)
            height_entry.insert(0,selected_value2[1])

        # プリセットメニュー
        preset_var = StringVar(resize_window)
        preset_var.set(self.presets[0][0])  # デフォルトは最初のプリセット
        preset_var.trace_add('write',preset_choice)
        Label(resize_window, text="プリセット:").grid(row=2, column=0, padx=10, pady=5)
        OptionMenu(resize_window, preset_var, *[p[0] for p in self.presets]).grid(row=2, column=1, padx=10, pady=5)
        # メインウインドウ側から設定を拾えるようにselfに代入
        self.height_entry = height_entry
        self.width_entry = width_entry


        def apply_size():
            try:
                # selected_preset = next((p for p in self.presets if p[0] == preset_var.get()), None)
                # if selected_preset:
                #     new_width, new_height = selected_preset[1], selected_preset[2]
                # else:
                new_width = int(width_entry.get())
                new_height = int(height_entry.get())
                # メインウインドウ側から設定を拾えるようにselfに代入
                self.height_entry = height_entry
                self.width_entry = width_entry
                # 赤枠のサイズを更新
                self.frame_width = new_width
                self.frame_height = new_height

                # 赤枠を再描画（スケールに合わせて調整）
                x1, y1, _, _ = self.canvas.coords(self.red_frame)
                scaled_width = self.frame_width * self.display_scale
                scaled_height = self.frame_height * self.display_scale
                self.canvas.coords(
                    self.red_frame,
                    x1,
                    y1,
                    x1 + scaled_width,
                    y1 + scaled_height
                )
                # print(f"Frame size updated to: {self.frame_width}x{self.frame_height}")
            except ValueError:
                print("Invalid input! Please enter numeric values.")

        Button(resize_window, text="Apply", command=apply_size).grid(row=3, column=0, columnspan=2, pady=10)
        return resize_window


if __name__ == "__main__":
    # root = Tk()
    root = TkinterDnD.Tk() 
    # ウィンドウサイズを調整
    root.geometry("1200x800")

    app = ImageCropperApp(root)
    root.mainloop()

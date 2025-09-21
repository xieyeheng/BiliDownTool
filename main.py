import requests
import os
import subprocess
import multiprocessing
import time
import customtkinter
import sys

def get_bvid_from_favlist(fav_list_id):
    """
    fav_list_id (str): Bilibili收藏夹的ID。
    """
    bvid_list = []
    page = 1
    has_more = True
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0'
    }

    print(f"开始获取收藏夹 ID: {fav_list_id} 中的视频信息...")

    while has_more:
        api_url = f"https://api.bilibili.com/x/v3/fav/resource/list?media_id={fav_list_id}&pn={page}&ps=20"
        
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data['code'] != 0:
                print(f"API请求失败，错误信息: {data['message']}")
                break
            medias = data['data']['medias']
            
            if not medias:
                print("没有更多视频了。")
                break

            for media in medias:
                bvid_list.append(media['bvid'])
            
            has_more = data['data']['has_more']
            page += 1

        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {e}")
            break
        except KeyError as e:
            print(f"解析JSON数据时发生键错误: {e}")
            break
        
    print("获取完成！")
    return bvid_list

def download_videos_from_list(bvid_list):
    """
    bvid_list (list): 包含所有视频BV号的列表。
    """
    download_dir = "Downloads"
    
    if not os.path.exists(download_dir):
        print(f"目录 '{download_dir}' 不存在，正在创建...")
        os.makedirs(download_dir)
    
    os.chdir(download_dir)
    
    print(f"\n开始下载视频到 '{os.getcwd()}' 目录...")
    
    for bvid in bvid_list:
        try:
            video_url = f"https://www.bilibili.com/video/{bvid}"
            print(f"正在下载视频: {video_url}")
            
            # -f bestvideo+bestaudio: 下载最高质量的视频和音频
            # --merge-output-format mp4: 合并视频和音频为mp4格式
            # -o "%(title)s.%(ext)s": 设置文件名格式为“视频标题.文件扩展名”

            subprocess.run(["yt-dlp", "-f", "bestvideo+bestaudio", "--merge-output-format", "mp4", video_url], check=True)
            
            print(f"视频 {bvid} 下载完成。")
            
            # 进行一个时间的延迟，防止请求过快被服务器屏蔽
            time.sleep(2)

        except FileNotFoundError:
            print("错误: 找不到 yt-dlp 命令。请确保你已经安装了yt-dlp并将其添加到了系统环境变量中。")
            print("你应该使用 'pip install yt-dlp' 来安装它。")
            os.chdir("..") 
            return
        except subprocess.CalledProcessError as e:
            print(f"下载视频 {bvid} 时发生错误: {e}")
        except Exception as e:
            print(f"处理视频 {bvid} 时发生未知错误: {e}")
    
    os.chdir("..")
    print("\n所有视频下载任务已完成！")


# cpp写多了就是想写全局变量
my_fav_list_id = ''
video_bvids = list()

# print(f"总共获取了 {len(video_bvids)} 个BV号。")
# print("BV号列表:", video_bvids)
# download_videos_from_list(video_bvids)


customtkinter.set_appearance_mode("System") 
# 可选值: "blue", "green", "dark-blue" (默认)
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bilibili 收藏夹下载工具")
        self.geometry("800x600")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, pady=20, padx=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.title_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")
        self.title_frame.grid_columnconfigure(0, weight=1)
        self.title_label = customtkinter.CTkLabel(
            self.title_frame, 
            text="Bilibili 收藏夹下载工具", 
            font=customtkinter.CTkFont(size=40, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        self.entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="嗯，就在这里输入收藏夹id吧")
        self.entry.grid(row=0, column=0, pady=10, padx=10, sticky="ew")
        self.button = customtkinter.CTkButton(self.main_frame, text="那么，开始下载吧！", command=self.button_callback)
        self.button.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        self.label = customtkinter.CTkLabel(self.main_frame, text="")
        self.label.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

    def button_callback(self):
        """
        当“确定”按钮被点击时执行的函数。
        """
        input_text = self.entry.get()
        if input_text:
            print(f"用户输入了: {input_text}")
            my_fav_list_id = input_text
            video_bvids = get_bvid_from_favlist(my_fav_list_id)
            process = multiprocessing.Process(target=download_videos_from_list, args=(video_bvids,))
            process.start()
            self.label.configure(text=f"已经在下载了，我懒得写进度条了，自己去终端看进度吧")
            
        else:
            print("好像没有输入")
            self.label.configure(text="你应该输入一些东西")
"""        process.join()
        print("下载进程结束")
        self.label.configure(text="下载进程结束")"""

if __name__ == "__main__":
    app = App()
    app.mainloop()
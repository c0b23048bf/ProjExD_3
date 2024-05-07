import os
import random
import sys
import time
import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 3
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんRect，または，爆弾Rect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.right < 0 or WIDTH < obj_rct.left:
        yoko = False
    if obj_rct.bottom < 0 or HEIGHT < obj_rct.top:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 2.0)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 1.0),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 1.0),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 1.0),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 1.0),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)
        
        
class Bomb:
    """
    爆弾に関するクラス
    """
    color_lst = [(255, 0, 0), (0, 255, 0), (0, 0, 255),(128, 128, 0), (0, 128, 128), (128, 0, 128)]
    delta_lst = [(+5, +5), (+5, -5), (-5, +5), (-5, -5), (0, +5), (+5, 0)]
    def __init__(self):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.rad = random.randint(5,10)
        self.img = pg.Surface((2*self.rad, 2*self.rad))
        pg.draw.circle(self.img, random.choice(__class__.color_lst), (self.rad, self.rad), self.rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = random.choice(__class__.delta_lst)

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Beam:
    """
    ビームに関するクラス
    """
    beam_img = pg.transform.rotozoom(pg.image.load("fig/beam.png"), 180, 2.0)
    img = pg.transform.flip(beam_img, True, False)
    
    def __init__(self, xy: tuple[int, int]):
        """
        ビーム画像Surfaceを生成する
        引数 xy：こうかとんの右座標がビームの左座標になるように
        """
        self.img = __class__.img
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.vx,self.vy = +5,0

    def update(self, screen: pg.Surface):
        """
        ビームをを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)
        

class Explosion:
    """
    爆発エフェクトに関するクラス
    """
    def __init__(self, xy: tuple[int, int]):
        self.img1 = pg.transform.rotozoom(pg.image.load("fig/explosion.gif"), 0, 2.0)
        self.img2 = pg.transform.flip(self.img1, True, True)
        self.rct1: pg.Rect = self.img1.get_rect()
        self.rct2: pg.Rect = self.img2.get_rect()
        self.ex_imgs = [self.img1, self.img2]
        self.ex_rcts = [self.rct1, self.rct2]
        self.rct1.center = xy
        self.rct2.center = xy
        self.life = 50
        self.a = 1
    
    def update(self, screen: pg.Surface):
        self.life -= 1
        if self.life > 0:
            if self.a >= 5:
                screen.blit(self.ex_imgs[0], self.ex_rcts[0])
            else:
                screen.blit(self.ex_imgs[1], self.ex_rcts[1])
            self.a += 1
            if self.a >= 10:
                self.a = 1
            

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((900, 400))
    bomb = [Bomb() for i in range(NUM_OF_BOMBS)]
    beam = None
    ex_lst = []
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        screen.blit(bg_img, [0, 0])
        
        for hk,j in enumerate(bomb):
            if j != None:
                if bird.rct.colliderect(j.rct):
                    # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    bomb[hk] = None
                    return
                
        for hj,n in enumerate(bomb):
            if (beam != None) and (n != None):
                if n.rct.colliderect(beam.rct):
                    # 爆弾とビームの衝突時に爆弾とビームを削除
                    bird.change_img(6, screen)
                    beam = None
                    bomb[hj] = None
                    ex_lst.append(Explosion((n.rct[0], n.rct[1])))
        
        if len(ex_lst) != 0:
            for hh,i in enumerate(ex_lst):
                if i.life > 0:
                    pass
                else:
                    del ex_lst[hh]
                i.update(screen)
                 
        key_lst = pg.key.get_pressed()
        if key_lst[pg.K_SPACE]:
            beam = Beam((bird.rct[0], bird.rct[1]))
        if beam != None:
            beam.update(screen)
        bird.update(key_lst, screen)
        for m in bomb:
            if m != None:
                m.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

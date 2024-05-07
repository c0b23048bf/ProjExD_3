import os
import random
import sys
import time
import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
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


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

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
    beam_img = pg.transform.rotozoom(pg.image.load("fig/beam.png"), 180, 2.0)  # デフォルトのこうかとん（右向き）
    img = pg.transform.flip(beam_img, True, False)
    
    def __init__(self, xy: tuple[int, int]):
        """
        ビーム画像Surfaceを生成する
        引数 xy：こうかとんの右座標がビームの左座標になるように
        """
        self.img = __class__.img
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = (xy[0],xy[1])
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
        
        
def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((900, 400))
    bomb = Bomb((255, 0, 0), 10)
    beam = None
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        screen.blit(bg_img, [0, 0])
        
        if bomb != None:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return
            
        if (beam != None) and (bomb != None):
            if bomb.rct.colliderect(beam.rct):
                # 爆弾とビームの衝突時に爆弾とビームを削除
                beam = None
                bomb = None
            
        key_lst = pg.key.get_pressed()
        if key_lst[pg.K_SPACE]:
            beam = Beam(bird.rct)
        if beam != None:
            beam.update(screen)
        bird.update(key_lst, screen)
        if bomb != None:
            bomb.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

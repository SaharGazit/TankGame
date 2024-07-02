import time

import pygame
from object import Object, Player, Powerup, Bullet, Block


class Game:

    def __init__(self, screen, client):
        self.screen = screen
        self.client = client
        if client is None:
            self.practice = True
        elif client.running_udp:
            self.practice = False
        else:
            self.practice = True

        self.exit_code = 0

    def main(self):  # (pygame is initialized beforehand)
        # object screen settings
        screen_size = self.screen.get_size()
        Object.screen_size = screen_size
        Object.scale_factor = (screen_size[0] / 1920, screen_size[1] / 1080)
        Object.screen = self.screen

        this_player = None
        other_players = []
        if not self.practice:
            # get starter position from server
            positions = self.client.get_buffer_data(False)
            start_position = [0, 0]
            for pos in positions:
                pos = pos.split('|')
                if pos[0] == self.client.name:
                    start_position = [int(pos[1]), int(pos[2])]

            # create player for each user
            for user in self.client.user_list[0] + self.client.user_list[1]:
                # create main player
                if user.name == self.client.name:
                    this_player = Player(user, start_position)
                # create other players
                else:
                    other_players.append(Player(user, [0, 0], False))

            # start voice listener
            self.client.start_voice_client()
        else:
            # in practice mode, use a dummy user to represent this player
            this_player = Player(self.client.get_dummy_user(), [0, 0])

        # objects currently on the map
        objects = [this_player, Block((4865, 4525), (140, 140), 'wall', 0), Block((1499, -3691), (151, 151), 'wall', 1),
                   Block((-4509, 107), (109, 109), 'wall', 2), Block((-2547, -3629), (52, 52), 'wall', 3),
                   Block((3910, 3368), (111, 111), 'wall', 4), Block((-2880, 4102), (188, 188), 'wall', 5),
                   Block((-2552, -1787), (112, 112), 'wall', 6), Block((3761, 3709), (177, 177), 'wall', 7),
                   Block((2345, 3658), (185, 185), 'wall', 8), Block((-4, -227), (97, 97), 'wall', 9),
                   Block((2000, 727), (104, 104), 'wall', 10), Block((-1647, -2190), (102, 102), 'wall', 11),
                   Block((1354, -1608), (169, 169), 'wall', 12), Block((-3955, -3948), (133, 133), 'wall', 13),
                   Block((-116, 3678), (121, 121), 'wall', 14), Block((930, 970), (83, 83), 'wall', 15),
                   Block((-2768, -63), (69, 69), 'wall', 16), Block((3413, 2060), (95, 95), 'wall', 17),
                   Block((4490, 4682), (197, 197), 'wall', 18), Block((633, 1430), (149, 149), 'wall', 19),
                   Block((496, 4572), (161, 161), 'wall', 20), Block((-733, 2409), (138, 138), 'wall', 21),
                   Block((1984, -2908), (86, 86), 'wall', 22), Block((2643, -2348), (154, 154), 'wall', 23),
                   Block((4620, 1542), (69, 69), 'wall', 24), Block((-3281, -3865), (62, 62), 'wall', 25),
                   Block((-4288, -3735), (190, 190), 'wall', 26), Block((-2555, 1927), (174, 174), 'wall', 27),
                   Block((-187, 327), (184, 184), 'wall', 28), Block((-3760, 1524), (78, 78), 'wall', 29),
                   Block((-1080, 51), (94, 94), 'wall', 30), Block((-2702, -3505), (91, 91), 'wall', 31),
                   Block((3941, 1911), (120, 120), 'wall', 32), Block((-2923, -3796), (189, 189), 'wall', 33),
                   Block((2818, -2491), (190, 190), 'wall', 34), Block((2358, 2222), (81, 81), 'wall', 35),
                   Block((-3839, -652), (152, 152), 'wall', 36), Block((-4047, 3897), (196, 196), 'wall', 37),
                   Block((-3722, -4), (123, 123), 'wall', 38), Block((-796, 1534), (146, 146), 'wall', 39),
                   Block((4216, 2923), (96, 96), 'wall', 40), Block((1002, -2445), (69, 69), 'wall', 41),
                   Block((211, -3393), (174, 174), 'wall', 42), Block((2588, 3168), (81, 81), 'wall', 43),
                   Block((-108, 876), (178, 178), 'wall', 44), Block((-1255, 3132), (100, 100), 'wall', 45),
                   Block((4106, 3782), (75, 75), 'wall', 46), Block((-95, 97), (96, 96), 'wall', 47),
                   Block((140, -4072), (171, 171), 'wall', 48), Block((3649, 380), (129, 129), 'wall', 49),
                   Block((-4030, 357), (98, 98), 'wall', 50), Block((-4595, 861), (185, 185), 'wall', 51),
                   Block((1790, 2487), (57, 57), 'wall', 52), Block((2628, 4668), (147, 147), 'wall', 53),
                   Block((-2943, -1858), (107, 107), 'wall', 54), Block((1510, 3381), (102, 102), 'wall', 55),
                   Block((-2336, 676), (75, 75), 'wall', 56), Block((3387, 115), (58, 58), 'wall', 57),
                   Block((-1790, 603), (92, 92), 'wall', 58), Block((-2589, -4287), (154, 154), 'wall', 59),
                   Block((1482, 1216), (78, 78), 'wall', 60), Block((-4966, 1632), (64, 64), 'wall', 61),
                   Block((-138, 1409), (192, 192), 'wall', 62), Block((1504, 3922), (54, 54), 'wall', 63),
                   Block((-4165, -3648), (187, 187), 'wall', 64), Block((-1854, -3367), (89, 89), 'wall', 65),
                   Block((-1061, -659), (112, 112), 'wall', 66), Block((1613, -1987), (52, 52), 'wall', 67),
                   Block((-2328, -1902), (119, 119), 'wall', 68), Block((-2644, 1473), (101, 101), 'wall', 69),
                   Block((-1243, 3185), (68, 68), 'wall', 70), Block((1683, -4886), (146, 146), 'wall', 71),
                   Block((4897, 2746), (59, 59), 'wall', 72), Block((-2097, 460), (143, 143), 'wall', 73),
                   Block((-1867, 3212), (193, 193), 'wall', 74), Block((-3619, -2959), (135, 135), 'wall', 75),
                   Block((4625, 3837), (153, 153), 'wall', 76), Block((-1200, 4888), (97, 97), 'wall', 77),
                   Block((-1874, 1380), (137, 137), 'wall', 78), Block((-4803, 4195), (169, 169), 'wall', 79),
                   Block((-2665, 2032), (139, 139), 'wall', 80), Block((4390, -3415), (164, 164), 'wall', 81),
                   Block((-1635, 1157), (142, 142), 'wall', 82), Block((662, -3095), (176, 176), 'wall', 83),
                   Block((1266, -4216), (86, 86), 'wall', 84), Block((-4077, 1912), (76, 76), 'wall', 85),
                   Block((3284, -3011), (168, 168), 'wall', 86), Block((256, 4293), (63, 63), 'wall', 87),
                   Block((3325, -1112), (158, 158), 'wall', 88), Block((204, -4447), (155, 155), 'wall', 89),
                   Block((847, -1616), (189, 189), 'wall', 90), Block((-3481, -2254), (106, 106), 'wall', 91),
                   Block((-1888, -344), (76, 76), 'wall', 92), Block((-2914, 263), (50, 50), 'wall', 93),
                   Block((-2752, 3756), (101, 101), 'wall', 94), Block((4136, -357), (107, 107), 'wall', 95),
                   Block((-592, -2876), (55, 55), 'wall', 96), Block((-1339, 2993), (133, 133), 'wall', 97),
                   Block((-2101, -1702), (141, 141), 'wall', 98), Block((-3587, 1714), (126, 126), 'wall', 99),
                   Block((2459, -2184), (139, 139), 'wall', 100), Block((363, -4780), (140, 140), 'wall', 101),
                   Block((1290, -1222), (194, 194), 'wall', 102), Block((-1073, -557), (198, 198), 'wall', 103),
                   Block((690, -1540), (146, 146), 'wall', 104), Block((-991, -1906), (194, 194), 'wall', 105),
                   Block((1577, -649), (121, 121), 'wall', 106), Block((-4452, -388), (91, 91), 'wall', 107),
                   Block((-1006, 55), (108, 108), 'wall', 108), Block((4573, -4044), (166, 166), 'wall', 109),
                   Block((-2967, 208), (186, 186), 'wall', 110), Block((2302, 1183), (70, 70), 'wall', 111),
                   Block((-1727, 338), (125, 125), 'wall', 112), Block((-2821, -2298), (58, 58), 'wall', 113),
                   Block((-2575, -1048), (113, 113), 'wall', 114), Block((-4665, 692), (102, 102), 'wall', 115),
                   Block((-4736, 837), (100, 100), 'wall', 116), Block((3725, -2499), (134, 134), 'wall', 117),
                   Block((-3926, 3748), (193, 193), 'wall', 118), Block((2255, -1055), (180, 180), 'wall', 119),
                   Block((4684, 4556), (155, 155), 'wall', 120), Block((-1675, -800), (173, 173), 'wall', 121),
                   Block((-2264, 361), (166, 166), 'wall', 122), Block((2436, 353), (104, 104), 'wall', 123),
                   Block((-475, -3145), (192, 192), 'wall', 124), Block((2355, -4532), (113, 113), 'wall', 125),
                   Block((-688, -4016), (200, 200), 'wall', 126), Block((3573, -171), (165, 165), 'wall', 127),
                   Block((3762, -1618), (175, 175), 'wall', 128), Block((3141, 2952), (154, 154), 'wall', 129),
                   Block((-3249, 4263), (183, 183), 'wall', 130), Block((-4403, 3820), (197, 197), 'wall', 131),
                   Block((4845, -257), (70, 70), 'wall', 132), Block((-11, -1050), (93, 93), 'wall', 133),
                   Block((-228, -1081), (194, 194), 'wall', 134), Block((-4990, 1286), (118, 118), 'wall', 135),
                   Block((-2656, 2680), (83, 83), 'wall', 136), Block((587, 3697), (184, 184), 'wall', 137),
                   Block((1182, -4804), (171, 171), 'wall', 138), Block((-4767, -3517), (164, 164), 'wall', 139),
                   Block((-4234, -1614), (137, 137), 'wall', 140), Block((-4759, 1342), (60, 60), 'wall', 141),
                   Block((-3291, -2104), (68, 68), 'wall', 142), Block((-4988, 2640), (186, 186), 'wall', 143),
                   Block((-2373, -1881), (124, 124), 'wall', 144), Block((4981, 4927), (102, 102), 'wall', 145),
                   Block((-1049, -4762), (63, 63), 'wall', 146), Block((1443, -4763), (114, 114), 'wall', 147),
                   Block((-705, 2711), (131, 131), 'wall', 148), Block((-1830, 3704), (64, 64), 'wall', 149),
                   Block((-2375, 4885), (60, 60), 'wall', 150), Block((-2244, 499), (189, 189), 'wall', 151),
                   Block((-3113, 1105), (66, 66), 'wall', 152), Block((-2385, -3287), (111, 111), 'wall', 153),
                   Block((2072, 4927), (102, 102), 'wall', 154), Block((-4533, -3406), (196, 196), 'wall', 155),
                   Block((2051, 3391), (142, 142), 'wall', 156), Block((-2316, 950), (99, 99), 'wall', 157),
                   Block((-1883, -2292), (107, 107), 'wall', 158), Block((2424, 2632), (169, 169), 'wall', 159),
                   Block((-4953, -1344), (109, 109), 'wall', 160), Block((1026, 1925), (151, 151), 'wall', 161),
                   Block((-3915, -707), (116, 116), 'wall', 162), Block((4698, 688), (174, 174), 'wall', 163),
                   Block((-4843, -2840), (172, 172), 'wall', 164), Block((-1176, 3495), (71, 71), 'wall', 165),
                   Block((-1025, -4519), (178, 178), 'wall', 166), Block((-3588, 769), (154, 154), 'wall', 167),
                   Block((-2652, 1759), (199, 199), 'wall', 168), Block((-1605, -1901), (78, 78), 'wall', 169),
                   Block((-4858, 2574), (157, 157), 'wall', 170), Block((-1364, -4102), (101, 101), 'wall', 171),
                   Block((-1864, 320), (189, 189), 'wall', 172), Block((-1390, 241), (138, 138), 'wall', 173),
                   Block((-1008, -2004), (92, 92), 'wall', 174), Block((480, -3950), (189, 189), 'wall', 175),
                   Block((-1684, -4930), (148, 148), 'wall', 176), Block((-1344, -4942), (126, 126), 'wall', 177),
                   Block((-2780, 1515), (197, 197), 'wall', 178), Block((-466, 594), (164, 164), 'wall', 179),
                   Block((-3160, -4470), (167, 167), 'wall', 180), Block((-2775, -4484), (171, 171), 'wall', 181),
                   Block((4656, -808), (144, 144), 'wall', 182), Block((-4263, -2165), (58, 58), 'wall', 183),
                   Block((1877, -1615), (67, 67), 'wall', 184), Block((-3120, -2499), (118, 118), 'wall', 185),
                   Block((-3669, -3251), (190, 190), 'wall', 186), Block((249, -3337), (134, 134), 'wall', 187),
                   Block((-4627, -2876), (131, 131), 'wall', 188), Block((-2069, 4890), (194, 194), 'wall', 189),
                   Block((3459, 3386), (109, 109), 'wall', 190), Block((-3913, 2952), (58, 58), 'wall', 191),
                   Block((-213, 3956), (125, 125), 'wall', 192), Block((-1300, -2269), (197, 197), 'wall', 193),
                   Block((3285, 4578), (157, 157), 'wall', 194), Block((-1496, 2761), (129, 129), 'wall', 195),
                   Block((658, -123), (86, 86), 'wall', 196), Block((2652, -1569), (146, 146), 'wall', 197),
                   Block((-4164, 3978), (168, 168), 'wall', 198), Block((2757, -461), (52, 52), 'wall', 199),
                   Block((1285, -2313), (73, 73), 'wall', 200), Block((-4618, -1969), (172, 172), 'wall', 201),
                   Block((746, 1781), (169, 169), 'wall', 202), Block((-4199, 4109), (165, 165), 'wall', 203),
                   Block((497, -678), (185, 185), 'wall', 204), Block((3655, 2301), (62, 62), 'wall', 205),
                   Block((-1005, -4260), (176, 176), 'wall', 206), Block((2153, 3296), (78, 78), 'wall', 207),
                   Block((3312, 2785), (163, 163), 'wall', 208), Block((3917, -1623), (102, 102), 'wall', 209),
                   Block((3824, -2322), (88, 88), 'wall', 210), Block((-1664, 979), (93, 93), 'wall', 211),
                   Block((1896, 4707), (53, 53), 'wall', 212), Block((-3462, 2035), (136, 136), 'wall', 213),
                   Block((4756, 721), (73, 73), 'wall', 214), Block((4026, 4999), (156, 156), 'wall', 215),
                   Block((2388, 29), (140, 140), 'wall', 216), Block((1850, 4404), (181, 181), 'wall', 217),
                   Block((3263, -537), (135, 135), 'wall', 218), Block((-4550, 3354), (102, 102), 'wall', 219),
                   Block((-127, 2234), (162, 162), 'wall', 220), Block((-235, 1596), (151, 151), 'wall', 221),
                   Block((3918, 541), (61, 61), 'wall', 222), Block((4230, -4609), (93, 93), 'wall', 223),
                   Block((1690, 1388), (159, 159), 'wall', 224), Block((2812, -4672), (90, 90), 'wall', 225),
                   Block((436, -2306), (170, 170), 'wall', 226), Block((2370, 1850), (180, 180), 'wall', 227),
                   Block((4553, 630), (71, 71), 'wall', 228), Block((-4126, 2324), (84, 84), 'wall', 229),
                   Block((1348, 4270), (50, 50), 'wall', 230), Block((-80, 3336), (50, 50), 'wall', 231),
                   Block((-89, -1057), (129, 129), 'wall', 232), Block((-4649, -2525), (50, 50), 'wall', 233),
                   Block((-1320, 586), (165, 165), 'wall', 234), Block((-1459, 4957), (69, 69), 'wall', 235),
                   Block((3771, -947), (157, 157), 'wall', 236), Block((-4681, -1926), (190, 190), 'wall', 237),
                   Block((-2764, -4468), (198, 198), 'wall', 238), Block((4780, 4696), (114, 114), 'wall', 239),
                   Block((3026, -4243), (112, 112), 'wall', 240), Block((2474, 478), (159, 159), 'wall', 241),
                   Block((939, 3562), (118, 118), 'wall', 242), Block((-4137, 4440), (156, 156), 'wall', 243),
                   Block((4506, -670), (52, 52), 'wall', 244), Block((-4392, -1906), (77, 77), 'wall', 245),
                   Block((-4410, 1549), (144, 144), 'wall', 246), Block((1056, -4012), (147, 147), 'wall', 247),
                   Block((3132, -760), (121, 121), 'wall', 248), Block((3222, -2157), (62, 62), 'wall', 249),
                   Block((-1786, -201), (171, 171), 'box', 250), Block((4307, -3402), (172, 172), 'box', 251),
                   Block((-4613, -4665), (105, 105), 'box', 252), Block((-509, -3281), (124, 124), 'box', 253),
                   Block((2516, 4803), (54, 54), 'box', 254), Block((3927, 2108), (53, 53), 'box', 255),
                   Block((-4011, 2508), (162, 162), 'box', 256), Block((-3096, -977), (137, 137), 'box', 257),
                   Block((-2283, -3259), (123, 123), 'box', 258), Block((1029, -4240), (99, 99), 'box', 259),
                   Block((2625, -269), (78, 78), 'box', 260), Block((-4123, 2175), (150, 150), 'box', 261),
                   Block((-3793, 3891), (180, 180), 'box', 262), Block((-2433, -1437), (180, 180), 'box', 263),
                   Block((-45, -2667), (189, 189), 'box', 264), Block((-2575, -3997), (121, 121), 'box', 265),
                   Block((-2371, -120), (156, 156), 'box', 266), Block((-3144, -303), (105, 105), 'box', 267),
                   Block((-890, 4529), (88, 88), 'box', 268), Block((-291, 3847), (187, 187), 'box', 269),
                   Block((-1504, -4167), (149, 149), 'box', 270), Block((563, -1133), (130, 130), 'box', 271),
                   Block((3565, -4307), (197, 197), 'box', 272), Block((-4800, -3009), (128, 128), 'box', 273),
                   Block((3692, -106), (145, 145), 'box', 274), Block((657, -3789), (162, 162), 'box', 275),
                   Block((925, -3479), (199, 199), 'box', 276), Block((4022, -473), (111, 111), 'box', 277),
                   Block((297, -774), (153, 153), 'box', 278), Block((-1159, 3345), (168, 168), 'box', 279),
                   Block((-4678, 2255), (173, 173), 'box', 280), Block((-2326, 2607), (72, 72), 'box', 281),
                   Block((-750, -2609), (107, 107), 'box', 282), Block((4114, -4367), (155, 155), 'box', 283),
                   Block((3142, 4547), (56, 56), 'box', 284), Block((-4351, -1916), (83, 83), 'box', 285),
                   Block((4612, -3408), (174, 174), 'box', 286), Block((1225, -244), (64, 64), 'box', 287),
                   Block((-1897, 1435), (144, 144), 'box', 288), Block((-2228, 72), (176, 176), 'box', 289),
                   Block((1115, 339), (200, 200), 'box', 290), Block((2709, 3662), (121, 121), 'box', 291),
                   Block((3551, 4482), (82, 82), 'box', 292), Block((664, -4130), (140, 140), 'box', 293),
                   Block((-716, -1175), (126, 126), 'box', 294), Block((719, -3313), (88, 88), 'box', 295),
                   Block((-3596, 2540), (87, 87), 'box', 296), Block((-1268, 3421), (185, 185), 'box', 297),
                   Block((-207, 247), (125, 125), 'box', 298), Block((4616, 453), (86, 86), 'box', 299),
                   Block((32, -3868), (64, 64), 'box', 300), Block((-4890, 3771), (141, 141), 'box', 301),
                   Block((3394, -4529), (164, 164), 'box', 302), Block((1573, -2785), (98, 98), 'box', 303),
                   Block((-2613, 4642), (186, 186), 'box', 304), Block((-1592, -4668), (149, 149), 'box', 305),
                   Block((2658, -613), (107, 107), 'box', 306), Block((-1500, 1918), (173, 173), 'box', 307),
                   Block((-3325, -112), (184, 184), 'box', 308), Block((4551, 2075), (78, 78), 'box', 309),
                   Block((1175, 2192), (158, 158), 'box', 310), Block((-3832, -2488), (127, 127), 'box', 311),
                   Block((1714, 1782), (81, 81), 'box', 312), Block((-510, -1822), (100, 100), 'box', 313),
                   Block((-1756, 4663), (52, 52), 'box', 314), Block((494, 2918), (112, 112), 'box', 315),
                   Block((-3240, -1029), (138, 138), 'box', 316), Block((2177, 4043), (162, 162), 'box', 317),
                   Block((2391, -2565), (171, 171), 'box', 318), Block((-2164, 770), (89, 89), 'box', 319),
                   Block((-2800, -1431), (82, 82), 'box', 320), Block((-200, -1601), (110, 110), 'box', 321),
                   Block((2727, 2575), (100, 100), 'box', 322), Block((341, 3799), (197, 197), 'box', 323),
                   Block((-3180, -3347), (67, 67), 'box', 324), Block((-1703, 2332), (150, 150), 'box', 325),
                   Block((1273, -1233), (121, 121), 'box', 326), Block((2257, -347), (94, 94), 'box', 327),
                   Block((-3438, -559), (58, 58), 'box', 328), Block((-554, -2146), (57, 57), 'box', 329),
                   Block((-3402, 2615), (51, 51), 'box', 330), Block((1625, 729), (170, 170), 'box', 331),
                   Block((-3739, 4093), (67, 67), 'box', 332), Block((231, 1628), (60, 60), 'box', 333),
                   Block((4390, 75), (162, 162), 'box', 334), Block((3938, 440), (156, 156), 'box', 335),
                   Block((4709, -2464), (86, 86), 'box', 336), Block((775, 3516), (66, 66), 'box', 337),
                   Block((2805, -4040), (86, 86), 'box', 338), Block((-418, -446), (76, 76), 'box', 339),
                   Block((-619, -2417), (61, 61), 'box', 340), Block((2889, 474), (183, 183), 'box', 341),
                   Block((4340, 1685), (96, 96), 'box', 342), Block((-3053, -685), (158, 158), 'box', 343),
                   Block((2331, 2213), (60, 60), 'box', 344), Block((2728, 2752), (128, 128), 'box', 345),
                   Block((2928, -3518), (99, 99), 'box', 346), Block((4937, -4865), (84, 84), 'box', 347),
                   Block((4369, -2775), (144, 144), 'box', 348), Block((592, -1999), (89, 89), 'box', 349),
                   Block((2781, 1397), (131, 131), 'box', 350), Block((-3551, 933), (64, 64), 'box', 351),
                   Block((4319, -976), (78, 78), 'box', 352), Block((-2263, -3768), (182, 182), 'box', 353),
                   Block((-4939, -3772), (140, 140), 'box', 354), Block((3387, -619), (109, 109), 'box', 355),
                   Block((4191, 2110), (92, 92), 'box', 356), Block((3753, -2984), (65, 65), 'box', 357),
                   Block((-4461, 1738), (129, 129), 'box', 358), Block((-1025, 623), (133, 133), 'box', 359),
                   Block((2215, -4943), (129, 129), 'box', 360), Block((-4572, 3852), (181, 181), 'box', 361),
                   Block((-135, 4032), (163, 163), 'box', 362), Block((-2078, 1887), (146, 146), 'box', 363),
                   Block((1713, -2741), (171, 171), 'box', 364), Block((-3485, 3651), (81, 81), 'box', 365),
                   Block((4923, 3457), (187, 187), 'box', 366), Block((-320, 16), (195, 195), 'box', 367),
                   Block((3751, 2925), (176, 176), 'box', 368), Block((1826, -1789), (125, 125), 'box', 369),
                   Block((3112, 3409), (50, 50), 'box', 370), Block((-2299, -163), (181, 181), 'box', 371),
                   Block((2086, -1079), (179, 179), 'box', 372), Block((-3993, 3970), (126, 126), 'box', 373),
                   Block((762, -2114), (169, 169), 'box', 374), Block((2050, -4013), (179, 179), 'box', 375),
                   Block((-3656, 1618), (80, 80), 'box', 376), Block((-171, 2882), (132, 132), 'box', 377),
                   Block((-2972, 129), (140, 140), 'box', 378), Block((-3440, 4297), (86, 86), 'box', 379),
                   Block((2189, 3664), (170, 170), 'box', 380), Block((-165, -1121), (191, 191), 'box', 381),
                   Block((1637, -1409), (186, 186), 'box', 382), Block((-659, -2812), (99, 99), 'box', 383),
                   Block((4990, -3146), (127, 127), 'box', 384), Block((2171, -2541), (148, 148), 'box', 385),
                   Block((-2533, -4480), (72, 72), 'box', 386), Block((1010, -504), (164, 164), 'box', 387),
                   Block((-4538, -454), (96, 96), 'box', 388), Block((-1452, -3399), (160, 160), 'box', 389),
                   Block((-2780, -3096), (177, 177), 'box', 390), Block((-1927, -402), (64, 64), 'box', 391),
                   Block((-1941, -2872), (177, 177), 'box', 392), Block((4768, 2322), (193, 193), 'box', 393),
                   Block((-990, 3032), (127, 127), 'box', 394), Block((2621, 4842), (159, 159), 'box', 395),
                   Block((-3471, 2796), (62, 62), 'box', 396), Block((2100, -2811), (165, 165), 'box', 397),
                   Block((-1313, 2488), (113, 113), 'box', 398), Block((4849, 2036), (166, 166), 'box', 399),
                   Block((-561, -4673), (113, 113), 'box', 400), Block((-447, 4061), (134, 134), 'box', 401),
                   Block((-2998, -3576), (152, 152), 'box', 402), Block((537, -556), (136, 136), 'box', 403),
                   Block((3695, 2756), (126, 126), 'box', 404), Block((523, -250), (79, 79), 'box', 405),
                   Block((1425, 4481), (75, 75), 'box', 406), Block((-1060, -4217), (179, 179), 'box', 407),
                   Block((-3217, -4382), (65, 65), 'box', 408), Block((2811, 2727), (170, 170), 'box', 409),
                   Block((-975, -862), (84, 84), 'box', 410), Block((963, 4752), (103, 103), 'box', 411),
                   Block((1251, 777), (175, 175), 'box', 412), Block((275, 4740), (199, 199), 'box', 413),
                   Block((-2658, -3005), (55, 55), 'box', 414), Block((1930, 516), (54, 54), 'box', 415),
                   Block((-2104, -751), (190, 190), 'box', 416), Block((4899, -507), (53, 53), 'box', 417),
                   Block((1084, -2681), (129, 129), 'box', 418), Block((4961, -1814), (166, 166), 'box', 419),
                   Block((-854, 1932), (99, 99), 'box', 420), Block((92, 804), (142, 142), 'box', 421),
                   Block((4391, 3104), (97, 97), 'box', 422), Block((-1960, -1473), (95, 95), 'box', 423),
                   Block((-910, 1219), (115, 115), 'box', 424), Block((1784, 1180), (101, 101), 'box', 425),
                   Block((-3638, 1707), (69, 69), 'box', 426), Block((3213, 3151), (130, 130), 'box', 427),
                   Block((4767, 2800), (114, 114), 'box', 428), Block((1408, -382), (114, 114), 'box', 429),
                   Block((-2591, -3346), (62, 62), 'box', 430), Block((3322, 2201), (199, 199), 'box', 431),
                   Block((-1995, 1792), (114, 114), 'box', 432), Block((-872, 4293), (64, 64), 'box', 433),
                   Block((2596, -1004), (59, 59), 'box', 434), Block((2087, -1189), (181, 181), 'box', 435),
                   Block((-3441, -334), (94, 94), 'box', 436), Block((-1492, -970), (83, 83), 'box', 437),
                   Block((-360, 24), (117, 117), 'box', 438), Block((-1035, 1117), (50, 50), 'box', 439),
                   Block((-2408, -2475), (141, 141), 'box', 440), Block((-288, 1920), (196, 196), 'box', 441),
                   Block((-1729, 44), (56, 56), 'box', 442), Block((4741, -4080), (169, 169), 'box', 443),
                   Block((-4537, -185), (94, 94), 'box', 444), Block((4038, 2899), (101, 101), 'box', 445),
                   Block((-2148, 2848), (53, 53), 'box', 446), Block((1296, 2381), (125, 125), 'box', 447),
                   Block((-2040, -3979), (196, 196), 'box', 448), Block((-3245, 3219), (84, 84), 'box', 449),
                   Block((4735, -331), (73, 73), 'box', 450), Block((-3463, -2755), (61, 61), 'box', 451),
                   Block((1428, -1311), (128, 128), 'box', 452), Block((149, -3805), (150, 150), 'box', 453),
                   Block((-1896, -3596), (70, 70), 'box', 454), Block((-3801, -670), (170, 170), 'box', 455),
                   Block((-2130, 3712), (137, 137), 'box', 456), Block((-4347, 1759), (70, 70), 'box', 457),
                   Block((-4565, 2232), (142, 142), 'box', 458), Block((3100, 3377), (80, 80), 'box', 459),
                   Block((-3297, -1193), (159, 159), 'box', 460), Block((-3068, -4963), (114, 114), 'box', 461),
                   Block((-159, 2105), (185, 185), 'box', 462), Block((3076, -854), (105, 105), 'box', 463),
                   Block((659, -3973), (131, 131), 'box', 464), Block((-4074, -4777), (73, 73), 'box', 465),
                   Block((-979, -3967), (61, 61), 'box', 466), Block((4629, 774), (74, 74), 'box', 467),
                   Block((1808, 1114), (78, 78), 'box', 468), Block((-1672, 4271), (104, 104), 'box', 469),
                   Block((-4922, 2377), (110, 110), 'box', 470), Block((3606, 2317), (88, 88), 'box', 471),
                   Block((-1109, 4779), (196, 196), 'box', 472), Block((2773, 1088), (138, 138), 'box', 473),
                   Block((-3658, 3859), (94, 94), 'box', 474), Block((-4105, 4255), (141, 141), 'box', 475),
                   Block((1438, 3932), (138, 138), 'box', 476), Block((4967, -385), (125, 125), 'box', 477),
                   Block((-3078, 353), (158, 158), 'box', 478), Block((329, -2037), (56, 56), 'box', 479),
                   Block((3277, -633), (179, 179), 'box', 480), Block((-981, -4018), (173, 173), 'box', 481),
                   Block((-2352, 3521), (187, 187), 'box', 482), Block((-4527, -4819), (185, 185), 'box', 483),
                   Block((3719, -883), (119, 119), 'box', 484), Block((3577, 421), (185, 185), 'box', 485),
                   Block((-503, -3353), (98, 98), 'box', 486), Block((2019, 1024), (87, 87), 'box', 487),
                   Block((-4727, 89), (153, 153), 'box', 488), Block((-397, -2210), (101, 101), 'box', 489),
                   Block((-2652, -2390), (87, 87), 'box', 490), Block((-2979, -2652), (54, 54), 'box', 491),
                   Block((2604, -1635), (96, 96), 'box', 492), Block((4356, -3062), (148, 148), 'box', 493),
                   Block((-4413, 4790), (96, 96), 'box', 494), Block((-2372, -401), (76, 76), 'box', 495),
                   Block((-2034, -4177), (152, 152), 'box', 496), Block((-3211, -1438), (88, 88), 'box', 497),
                   Block((-947, 415), (157, 157), 'box', 498), Block((-2898, -4328), (146, 146), 'box', 499),
                   Powerup((-866, -380), 'strength'), Powerup((-4576, 3613), 'strength'),
                   Powerup((2045, -3305), 'heal'), Powerup((990, 1114), 'heal'), Powerup((-833, 3023), 'heal'),
                   Powerup((1343, 332), 'strength'), Powerup((-4114, -3090), 'speed'), Powerup((-531, 3996), 'speed'),
                   Powerup((-4794, 3828), 'heal'), Powerup((3613, -3939), '1up'), Powerup((-2644, 4103), '1up'),
                   Powerup((-4237, 2300), '1up'), Powerup((4355, 4566), 'heal'), Powerup((-4693, 2118), 'heal'),
                   Powerup((4734, -3478), '1up'), Powerup((-4861, 0), '1up'), Powerup((-4405, -2738), 'heal'),
                   Powerup((-4375, -3509), 'speed'), Powerup((4970, 3847), '1up'), Powerup((1086, -3297), 'heal'),
                   Powerup((-3371, -1221), 'strength'), Powerup((-4189, 3659), '1up'),
                   Powerup((-921, -4539), 'strength'), Powerup((-283, -4884), '1up'), Powerup((-3481, 2679), 'heal'),
                   Powerup((-490, 2089), 'heal'), Powerup((191, -823), 'strength'), Powerup((-4075, 1029), 'strength'),
                   Powerup((218, -392), 'strength'), Powerup((4750, -3013), '1up'), Powerup((251, 3474), '1up'),
                   Powerup((1155, 1657), 'strength'), Powerup((4515, -4848), 'strength'), Powerup((721, 4908), '1up'),
                   Powerup((71, 246), 'speed'), Powerup((4466, 3006), '1up'), Powerup((-686, 35), 'heal'),
                   Powerup((-551, -374), '1up'), Powerup((-4106, -3790), '1up'), Powerup((1280, 4290), '1up'),
                   Powerup((-1170, 1460), '1up'), Powerup((-1847, -4713), '1up'), Powerup((3602, 410), 'speed'),
                   Powerup((-1154, 393), 'speed'), Powerup((-697, 4734), 'heal'), Powerup((-1847, 3088), '1up'),
                   Powerup((2988, 30), 'speed'), Powerup((-4754, 2077), 'heal'), Powerup((1655, 3134), '1up'),
                   Powerup((-2305, -144), 'speed'), Powerup((-3919, -1278), 'strength'),
                   Powerup((-4006, 4494), 'speed'), Powerup((-1903, -3063), 'speed'), Powerup((1931, -2744), '1up'),
                   Powerup((302, -2203), 'heal'), Powerup((216, 3453), '1up'), Powerup((2490, 2982), 'strength'),
                   Powerup((3179, -3014), 'speed'), Powerup((1517, 3620), 'heal'), Powerup((-4057, -3919), 'strength'),
                   Powerup((4658, -3119), 'strength'), Powerup((4945, 2853), 'heal'), Powerup((2690, 2515), '1up'),
                   Powerup((-5000, -2657), 'heal'), Powerup((-4922, 3563), '1up'), Powerup((3151, -4478), 'heal'),
                   Powerup((3726, -3860), '1up'), Powerup((1071, -229), 'speed'), Powerup((-4378, -3071), '1up'),
                   Powerup((-226, -1189), 'heal'), Powerup((2362, 2121), 'strength'),
                   Powerup((2436, -4292), 'strength'), Powerup((4779, -2809), 'heal'), Powerup((-908, 2459), 'heal'),
                   Powerup((3565, 4799), 'speed'), Powerup((3531, 1100), '1up'), Powerup((-2222, 3323), '1up'),
                   Powerup((4469, 2611), '1up'), Powerup((3629, 1492), 'heal'), Powerup((2094, 1953), 'heal'),
                   Powerup((3438, -2325), '1up'), Powerup((707, -279), 'speed'), Powerup((3860, 3052), 'speed'),
                   Powerup((-3570, 3312), 'speed'), Powerup((-377, 3235), 'strength'), Powerup((-175, 3989), 'speed'),
                   Powerup((2042, -1210), 'strength'), Powerup((3978, -1714), 'heal'), Powerup((2405, -3614), 'speed'),
                   Powerup((2387, -3030), 'strength'), Powerup((-3028, 147), '1up'), Powerup((324, 4124), 'strength'),
                   Powerup((2356, 2235), 'strength'), Powerup((-3267, 1622), '1up'), Powerup((-3968, 1955), 'speed'),
                   Powerup((-3541, -2188), 'speed'), Powerup((693, -665), 'speed'), Powerup((-3791, 3503), 'speed'),
                   Powerup((-918, 2022), '1up'), Powerup((-3564, 642), '1up'), Powerup((-3603, -1527), 'strength'),
                   Powerup((-4063, -1723), 'strength'), Powerup((2929, 3425), 'heal'), Powerup((3105, -3928), 'heal'),
                   Powerup((1728, 1616), 'strength'), Powerup((-3278, 3990), 'heal'), Powerup((-3347, -543), 'heal'),
                   Powerup((1538, -4542), 'strength'), Powerup((-1994, 862), 'heal'), Powerup((-4697, 737), 'strength'),
                   Powerup((-3486, -4217), '1up'), Powerup((-4913, 956), 'heal'), Powerup((4241, 4538), 'speed'),
                   Powerup((4897, 666), 'speed'), Powerup((4541, -3003), 'heal'), Powerup((-3699, 3400), '1up'),
                   Powerup((2607, -1748), 'speed'), Powerup((996, 1600), 'heal'), Powerup((1785, -4284), 'strength'),
                   Powerup((-1395, -4084), '1up'), Powerup((4576, 2466), 'speed'), Powerup((-2534, -4476), 'strength'),
                   Powerup((-1915, 4556), '1up'), Powerup((-1927, 3275), '1up'), Powerup((-3575, 4306), '1up'),
                   Powerup((-3438, 4157), 'strength'), Powerup((1047, 4856), 'speed'), Powerup((394, 1175), 'speed'),
                   Powerup((3920, 4014), 'strength'), Powerup((913, -3174), 'heal'), Powerup((-2821, -3232), 'speed'),
                   Powerup((-688, -4213), 'heal'), Powerup((1208, 3611), 'speed'), Powerup((-1753, 671), 'heal'),
                   Powerup((4976, 3487), 'speed'), Powerup((4782, 3591), 'heal'), Powerup((630, 2827), '1up'),
                   Powerup((-1354, 2615), 'speed'), Powerup((-3589, -23), 'speed'), Powerup((4756, -4543), 'heal'),
                   Powerup((192, 2582), '1up'), Powerup((2521, 3018), 'strength'), Powerup((-441, 1520), '1up'),
                   Powerup((-2368, 393), 'heal'), Powerup((3257, 2546), 'heal'), Powerup((49, 4314), 'strength'),
                   Powerup((492, -329), 'strength'), Powerup((-1179, -574), '1up'), Powerup((-4509, -2183), '1up'),
                   Powerup((853, -4089), '1up'), Powerup((2903, -2790), '1up'), Powerup((754, 3442), '1up'),
                   Powerup((-1997, -3079), '1up'), Powerup((1796, 351), 'heal'), Powerup((2157, 2867), 'heal'),
                   Powerup((-4369, -3131), 'heal'), Powerup((3842, -3256), '1up'), Powerup((4970, -2848), 'speed'),
                   Powerup((6, 2638), 'heal'), Powerup((-346, -2047), 'heal'), Powerup((-1387, 891), 'strength'),
                   Powerup((4936, -3530), '1up'), Powerup((264, 1482), 'strength'), Powerup((1975, -2567), 'speed'),
                   Powerup((-3223, 4871), '1up'), Powerup((4482, -411), '1up'), Powerup((2860, 4345), 'strength'),
                   Powerup((-4227, -2160), '1up'), Powerup((2881, 4153), 'strength'), Powerup((-359, -1136), '1up'),
                   Powerup((-1704, 325), 'speed'), Powerup((-2028, 3205), 'heal'), Powerup((-1222, 1103), 'heal'),
                   Powerup((-1067, 1110), 'strength'), Powerup((-2685, -3992), 'strength'),
                   Powerup((-3144, -1886), 'heal'), Powerup((13, -3960), '1up'), Powerup((-14, 4008), '1up'),
                   Powerup((4808, 4522), 'speed'), Powerup((-2543, -3716), 'heal'), Powerup((-3422, -2281), 'strength'),
                   Powerup((-3941, -4838), '1up'), Powerup((-1696, -3932), 'speed'), Powerup((1332, -1163), '1up'),
                   Powerup((4090, -87), 'heal'), Powerup((2152, -4373), 'strength'), Powerup((2142, -805), 'speed'),
                   Powerup((-528, -2372), 'speed'), Powerup((-2129, -304), 'strength'), Powerup((-2086, 168), '1up'),
                   Powerup((-2864, -2474), '1up'), Powerup((-4953, 13), 'speed'), Powerup((-2318, 1049), 'strength'),
                   Powerup((610, -3370), 'heal'), Powerup((-872, 3133), 'heal'), Powerup((-1152, -1755), 'speed'),
                   Powerup((3580, -3169), '1up'), Powerup((472, -1079), '1up'), Powerup((-3312, -2989), 'speed'),
                   Powerup((-1539, -1181), 'strength'), Powerup((-3293, 2289), 'strength'),
                   Powerup((-3272, 1811), '1up'), Powerup((2785, 2247), 'strength'), Powerup((-2359, 85), 'speed'),
                   Powerup((-2402, 4561), 'strength'), Powerup((-4196, -1897), 'speed'),
                   Powerup((-2338, 3266), 'speed'), Powerup((-2203, -4612), 'speed'), Powerup((453, 3477), 'strength'),
                   Powerup((-128, 2470), 'speed'), Powerup((-296, 3233), 'heal'), Powerup((4223, 4839), 'strength'),
                   Powerup((3801, -688), 'strength'), Powerup((890, -1284), 'heal'), Powerup((-2392, 684), '1up'),
                   Powerup((-3863, 3409), 'heal'), Powerup((-2129, 391), 'heal'), Powerup((4670, -916), '1up'),
                   Powerup((2288, 1103), 'speed'), Powerup((4735, -289), '1up'), Powerup((-3803, -3660), 'strength'),
                   Powerup((2411, 494), '1up'), Powerup((-1843, -5), '1up'), Powerup((4620, -482), 'strength'),
                   Powerup((-3933, 978), 'heal'), Powerup((4631, -50), 'strength'), Powerup((-4309, -2218), '1up'),
                   Powerup((-451, -2785), 'heal'), Powerup((-4515, -4939), '1up'), Powerup((939, 2256), 'heal'),
                   Powerup((3301, 1176), 'strength'), Powerup((-1016, -3156), 'strength'),
                   Powerup((-2129, 3036), '1up'), Powerup((154, 2388), 'strength'), Powerup((-3534, 4290), 'speed'),
                   Powerup((-3411, 4704), 'speed'), Powerup((-1986, 295), 'strength'), Powerup((1112, 2663), '1up'),
                   Powerup((3907, 4710), 'speed'), Powerup((-2853, 1127), 'speed'), Powerup((-4888, -112), 'strength'),
                   Powerup((-3030, -403), 'heal'), Powerup((-3066, 188), '1up'), Powerup((1544, -153), '1up'),
                   Powerup((3746, -2274), 'speed'), Powerup((1459, 4255), 'speed'), Powerup((3375, 2657), '1up'),
                   Powerup((4616, -4507), 'heal'), Powerup((-627, -3803), 'heal'), Powerup((-2410, 3408), '1up')]

        # clock
        clock = pygame.time.Clock()

        # victory screen
        win_conditions = [False, False]
        v_time = None

        # main game loop
        while self.exit_code == 0:
            for event in pygame.event.get():
                # if user closes the window, stop the game from running.
                if event.type == pygame.QUIT:
                    self.exit_code = -1

                # WASD keys for moving with the player. the player receives acceleration by pressing down a key.
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        this_player.add_force(0)
                    if event.key == pygame.K_d:
                        this_player.add_force(1)
                    if event.key == pygame.K_s:
                        this_player.add_force(2)
                    if event.key == pygame.K_a:
                        this_player.add_force(3)
                    if event.key == pygame.K_k:
                        this_player.global_position[1] -= 10  # temp

                # the player loses acceleration (accelerated backwards) by un-pressing a key
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        this_player.add_force(2)
                    if event.key == pygame.K_d:
                        this_player.add_force(3)
                    if event.key == pygame.K_s:
                        this_player.add_force(0)
                    if event.key == pygame.K_a:
                        this_player.add_force(1)

                    # pressing escape will also exit the game
                    if event.key == pygame.K_ESCAPE:
                        # TODO: pause menu
                        self.exit_code = 1

                # pressing left mouse buttons shoots a bullet
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and this_player.alive:  # (1 = left mouse click)
                        # creates a bullet with the position and rotation of the player, and creates a bullet shoot event
                        objects.append(Bullet(this_player))
                        if not self.practice:
                            self.trigger_event("shoot")

            # game remains at 60 FPS
            clock.tick(80)
            # clears out the screen every game loop
            self.screen.fill((159, 168, 191))

            if not self.practice:
                # server data handling
                for data in self.client.get_buffer_data():

                    # if the message starts with G, it is a player update
                    if data[0] == "G":
                        data = data.split('|')
                        # find right player
                        for player in other_players:
                            if player.user.name == data[1]:
                                # update player position and rotation
                                player.global_position = [float(data[2]), float(data[3])]
                                player.rotation = float(data[4])
                                break

                    # if the message starts with L, it is a lobby update
                    elif data[0] == "L":
                        self.client.update_lobby(data)

                        # remove players the no longer exist (they left)
                        for player in other_players:
                            if player.user not in self.client.user_list[0] + self.client.user_list[1]:
                                other_players.remove(player)

                    # handle events
                    elif data[0] == 'E':
                        data = data.split("|")
                        # shooting
                        if data[1] == 's':
                            for p in other_players:
                                if p.user.name == data[2]:
                                    objects.append(Bullet(p))

                    else:
                        print(data)

                # send personal data to server
                self.client.send_player_status(f"{round(this_player.global_position[0], 2)}|{round(this_player.global_position[1], 2)}|{round(this_player.rotation, 2)}|")

                # trigger victory
                if this_player.winner is None:
                    # trigger victory screen if win condition is met
                    if win_conditions[0]:
                        this_player.winner = "red"
                        v_time = time.perf_counter()
                    elif win_conditions[1]:
                        this_player.winner = "blue"
                        v_time = time.perf_counter()

                # victory screen timer
                else:
                    # leave the game 7 seconds after message is displayed
                    if time.perf_counter() > v_time + 7:
                        self.exit_code = 1

            # handling objects
            win_conditions = [True, True]
            for o in objects[1:] + other_players + [this_player]:  # the players are "pushed" to the end in order to draw them last

                # prevents the object from colliding with itself
                potential_collisions = list(objects + other_players)
                potential_collisions.remove(o)

                o.update(potential_collisions)

                # destroy object if needed by removing it from the objects list
                if o.to_destroy:
                    if o in objects:
                        objects.remove(o)
                    elif o in other_players:
                        other_players.remove(o)

                # draw object if it's inside the screen
                if o.in_screen():
                    if type(o) == Player:
                        # avoid drawing a player if they are a ghost (and this player isn't one)
                        if o.alive or not this_player.alive:
                            o.draw_object()
                    else:
                        o.draw_object()

                # check win condition
                if type(o) == Player and not self.practice:
                    if o.alive:
                        win_conditions[o.user.team - 1] = False

            # update screen
            pygame.display.flip()

        if self.exit_code == 1 and not self.practice:
            # disconnect from udp server, if it opened
            self.client.disconnect_udp()
            self.client.stop_voice_client()
            # notify server about leaving the game
            self.client.send_data("main")

        # return exit code to the lobby when the main loop is over
        return self.exit_code

    def trigger_event(self, action):
        self.client.send_data(f"E|{action[0]}")
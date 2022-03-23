import os

import pooch

registry = {
    '20091021202517-01000100-VIS_0001.ntf': 'sha512:3d7e07f987e18fcaec81c13405b75bf285e6bf65ff7ed77d4d37fa3c1d43abbd1208eb849cbfbca77317096c8e9a2a6284c977662be19e9c840cc6397f0c31f1',
    'aerial_rgba_000003.tiff': 'sha512:c680e44598728c7a95e98a4dc665873856b889bf186bbdc682beb43d3c4824a4c00adaa23613aeca497b9508934dad63bf4a00e0113ba5620b19d7b2bbb141d0',
    'cclc_schu_100.tif': 'sha512:3435dc29da9f854da9b145058dfcacc65c9c78d1664af9a225f0ece07e16a950ae5da7eae1352cd167b5a330da532f58a1aa315be205132a7766650f2c2bffb2',
    'landcover_sample_2000.tif': 'sha512:61d037022168eb640368f256851d9827d10cb69f46921d7063a62b632f95ec0b8a35b2e0521853e62522f16e91a98cecd0099bd0887995be66d42bf815c783e9',
    'paris_france_10.tiff': 'sha512:16073b737ba055031918659aad3ec9f7daeea88c94d83b86d7de1026a09e5bd741fa03bd96f4fbd3438952d661e7cbe33937ceaec05771ed0f13f020f6865d1f',
    'rgb_geotiff.tiff': 'sha512:2be5c8ab1b95a0dd835b278715093374020cb52b626345775d207c24d0b0c915dba587d62bbb186671fa5c64b7e9bc017c53e0b186ba744dd990892f91ee7a0f',
    'RomanColosseum_WV2mulitband_10.tif': 'sha512:9fd95ba26bad88a4e10a53685c531134528008607155c2de69ef4598b73b69450fc1fa672345e62696cbf71dd84489f744407b3152815ed43fc20375d26c7bee',
    'Elevation.tif': 'sha512:44587c3b00d349344bcec5cefd3bcda9fcef5e9bbdd0f1a2a4ce76016fa0bb68436ac206c96f54d6a828b45db212aa9d43410dbf40a61ba1d8eec934f7070250',
    'TC_NG_SFBay_US_Geo.tif': 'sha512:da2e66528f77a5e10af5de9e496074b77277c3da81dafc69790189510e5a7e18dba9e966329d36c979f1b547f0d36a82fbc4cfccc65ae9ef9e2747b5a9ee77b0',
    'astro.png': 'sha512:de64fcb37e67d5b5946ee45eb659436b446a9a23ac5aefb6f3cce53e58a682a0828f5e8435cf7bd584358760d59915eb6e37a1b69ca34a78f3d511e6ebdad6fd',
    'afie_1.jpg': 'sha512:88a2da3313df5a9422ab1cbc9a4b5715a7b5357923a938841f105de546c8d7380f689694cf3314621684ddd9216289764e6f488329ceb1f2ed0716213603b619',
    'afie_2.jpg': 'sha512:b64261c8a9ea586a79aa87926ffd44499cd719ea21dd0ba82883d4108e3186faf9d77570a70f4bb88e40b66f3d341f1cf8a9524cb38b2038cad7031b037805d6',
    'afie_3.jpg': 'sha512:fb1621f28ed6daee0d66a601c9b8a0ab9f7a75cf30bb487a558e4883b1ad9c6e891068be4f067f5046ac28c5ce418c39117165d20389b8eff9bb80b8e778acb4',
    'envi_rgbsmall_bip.hdr': 'sha512:5dcd18462be5c569cf80fde5334bb9a47cb91f853cdd01c2c3b899dbce1db91ac27c266d879436497f7c3e64d00331022793f510b786118065083e79f1aba8a7',
    'envi_rgbsmall_bip.img': 'sha512:eff9dcc3f5fdae898132ccb908ee0c13725f2b8178871b2c158ffe6f3306ba1408da59fde9228df6ed7ef9b1b720805a3fb5df4545eb80c640d221a7ee697a31',
    'IHTest_202009_Path3_Step5_BBXSWIR_12deg_DistStA.hdr': 'sha512:d8e11e23d81f397a895d8e302258805082fec9358d44baa63c971c56aecfc725fa0458ff86f2aa64c23c3461dd60d287c28af687393af853d2c1d2b4513163fa',
    'IHTest_202009_Path3_Step5_BBXSWIR_12deg_DistStA.raw': 'sha512:8cb5a57c37c87e8a45d51a6d5e5b072a488b79ade82dcfc227473dd60a66cd5fb980a84b59e7541ed5cbfac52605d84ed0b8f055b8da7223d420d69faafe6abd',
    'HTA9_1_BA_F_ROI02.ome.tif': 'sha512:e30b2c307538107b905e1ff7f674a1fca0ee298df0280fcad411a4adf69d684a34b6b9c1a516054e7f54b8a2b60c886b3874fce28e7cd90e14c3dac2a9a210ef',
}


class DKCPooch(pooch.Pooch):
    def get_url(self, fname):
        self._assert_file_in_registry(fname)
        algo, hashvalue = self.registry[fname].split(':')
        return self.base_url.format(algo=algo, hashvalue=hashvalue)


# path = pooch.cache_location(pooch.os_cache('geodata'), None, None)
datastore = DKCPooch(
    path=pooch.utils.cache_location(
        os.path.join(
            os.environ.get('TOX_WORK_DIR', pooch.utils.os_cache('pooch')),
            'django_large_image_datastore',
        )
    ),
    base_url='https://data.kitware.com/api/v1/file/hashsum/{algo}/{hashvalue}/download',
    registry=registry,
)

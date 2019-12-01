from vosim.server import init_server

def test_get_assets_url():
    app = init_server()
    assert app.get_asset_url('styles.css') == '/vosim/assets/styles.css'

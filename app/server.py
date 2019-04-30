from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, FileResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn, aiohttp, asyncio
from io import BytesIO
from cnnDetect import unetCountEggs

from fastai import *
from fastai.vision import *

def acc_camvid(input, target):
    target = target.squeeze(1)
    return (input.argmax(dim=1)==target).float().mean()


# export_file_url = 'https://www.dropbox.com/s/v6cuuvddq73d1e0/export.pkl?raw=1'
# export_file_url = 'https://www.dropbox.com/s/6bgq8t6yextloqp/export.pkl?raw=1'
export_file_url = 'https://www.dropbox.com/s/09ktpofemk7uf06/egg_export-800.pkl?raw=1'
export_file_name = 'egg_export-800.pkl'

classes = ['black', 'grizzly', 'teddys']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))
app.mount('/data', StaticFiles(directory='app/data'))

async def download_file(url, dest):
    if dest.exists(): return
    print(f'Downloading {export_file_name}')
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f: f.write(data)

async def setup_learner():
    await download_file(export_file_url, path/export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        defaults.device = torch.device('cpu')
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/')
def index(request):
    html = path/'view'/'index.html'
    return HTMLResponse(html.open().read())

@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    img_bytes = await (data['file'].read())
    img = open_image(BytesIO(img_bytes))
    p_img = unetCountEggs(learn, img.data.numpy().transpose(1,2,0))  
    PIL.Image.fromarray((255*p_img).astype(np.uint8)).save(f'app/data/p_img.jpg')
    return(FileResponse('app/data/p_img.jpg'))

@app.route('/analyzeTest', methods=['POST'])
async def analyzeTest(request):
    img = open_image('app/data/testImage.jpg')
    p_img = unetCountEggs(learn, img.data.numpy().transpose(1,2,0))  
    PIL.Image.fromarray((255*p_img).astype(np.uint8)).save(f'app/data/p_img.jpg')
    return(FileResponse('app/data/p_img.jpg'))

@app.route('/test', methods=['GET'])
async def test(request):
    return(FileResponse('app/data/testImage.jpg'))

if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app=app, host='0.0.0.0', port=5042)

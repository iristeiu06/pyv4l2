import sys
import v4l2
import v4l2.uapi
from cam_helpers import merge_configs

MEDIA_DEVICE_NAME = ('rp1-cfe', 'model')
DESER_REGEX = '(max96724|max96726a|max9296a) [0-9]+-[a-f0-9]+'
CSI2_NAME = 'csi2'

# Pixel

ov5640_w = 1280
ov5640_h = 720

ov5640_bus_fmt = v4l2.BusFormat.UYVY8_1X16
ov5640_pix_fmt = v4l2.PixelFormats.UYVY

mbus_fmt_ov5640 = (ov5640_w, ov5640_h, ov5640_bus_fmt)
fmt_pix = (ov5640_w, ov5640_h, ov5640_pix_fmt)

# TPG

mbus_fmt_tpg = (640, 480, v4l2.BusFormat.RGB888_1X24)
fmt_tpg = (640, 480, v4l2.PixelFormats.BGR888)


def gen_ov5640_pixel(des_ent, des_src_pad, ch_index, cameras, port):
    sensor_ent = cameras[port][1]
    ser_ent = cameras[port][0]

    return {
        'media': MEDIA_DEVICE_NAME,

        'subdevs': [
            # Camera
            {
                'entity': sensor_ent,
                'pads': [
                    { 'pad': (0, 0), 'fmt': mbus_fmt_ov5640 },
                ],
            },

            # Serializer
            {
                'entity': ser_ent,
                'routing': [
                    { 'src': (0, 0), 'dst': (1, 0) },
                ],
                'pads': [
                    { 'pad': (0, 0), 'fmt': mbus_fmt_ov5640 },
                    { 'pad': (1, 0), 'fmt': mbus_fmt_ov5640 },
                ],
            },
            # Deserializer
            {
                'entity': des_ent,
                'routing': [
                    { 'src': (port, 0), 'dst': (des_src_pad, port) },
                ],
                'pads': [
                    { 'pad': (port, 0), 'fmt': mbus_fmt_ov5640 },
                    { 'pad': (des_src_pad, port), 'fmt': mbus_fmt_ov5640 },
                ],
            },

            # CSI-2 RX
            {
                'entity': CSI2_NAME,
                'routing': [
                    { 'src': (0, port), 'dst': (1 + ch_index, 0) },
                ],
                'pads': [
                    { 'pad': (0, port), 'fmt': mbus_fmt_ov5640 },
                    { 'pad': (1 + ch_index, 0), 'fmt': mbus_fmt_ov5640 },
                ],
            },
        ],

        'devices': [
            {
                'entity': f'rp1-cfe-csi2-ch{ch_index}',
                'fmt': fmt_pix,
                'kms-format': v4l2.PixelFormats.RGB565,
            },
        ],

        'links': [
            { 'src': (sensor_ent, 0), 'dst': (ser_ent, 0) },
            { 'src': (ser_ent, 1), 'dst': (des_ent, port) },
            { 'src': (des_ent, des_src_pad), 'dst': (CSI2_NAME, 0) },
            { 'src': (CSI2_NAME, 1 + ch_index), 'dst': (f'rp1-cfe-csi2-ch{ch_index}', 0) },
        ],
    }


def gen_des_tpg(des_ent, des_src_pad, ch_index):
    return {
        'media': MEDIA_DEVICE_NAME,

        'subdevs': [
            # Deserializer
            {
                'entity': des_ent,
                'routing': [
                    { 'src': (8, 0), 'dst': (des_src_pad, 0) },
                ],
                'pads': [
                    { 'pad': (8, 0), 'fmt': mbus_fmt_tpg },
                    { 'pad': (des_src_pad, 0), 'fmt': mbus_fmt_tpg },
                ],
            },

            # CSI-2 RX
            {
                'entity': CSI2_NAME,
                'routing': [
                    { 'src': (0, 0), 'dst': (1 + ch_index, 0) },
                ],
                'pads': [
                    { 'pad': (0, 0), 'fmt': mbus_fmt_tpg },
                    { 'pad': (1 + ch_index, 0), 'fmt': mbus_fmt_tpg },
                ],
            },
        ],

        'devices': [
            {
                'entity': f'rp1-cfe-csi2-ch{ch_index}',
                'fmt': fmt_tpg,
            },
        ],

        'links': [
            { 'src': (des_ent, des_src_pad), 'dst': (CSI2_NAME, 0) },
            { 'src': (CSI2_NAME, 1 + ch_index), 'dst': (f'rp1-cfe-csi2-ch{ch_index}', 0) },
        ],
    }

def gen_ser_tpg(des_ent, des_src_pad, ch_index, cameras, port):
    ser_ent = cameras[port][0]

    return {
        'media': MEDIA_DEVICE_NAME,

        'subdevs': [
            # Serializer
            {
                'entity': ser_ent,
                'routing': [
                    { 'src': (2, 0), 'dst': (1, 0) },
                ],
                'pads': [
                    { 'pad': (2, 0), 'fmt': mbus_fmt_tpg },
                    { 'pad': (1, 0), 'fmt': mbus_fmt_tpg },
                ],
            },
            # Deserializer
            {
                'entity': des_ent,
                'routing': [
                    { 'src': (port, 0), 'dst': (des_src_pad, port) },
                ],
                'pads': [
                    { 'pad': (port, 0), 'fmt': mbus_fmt_tpg },
                    { 'pad': (des_src_pad, port), 'fmt': mbus_fmt_tpg },
                ],
            },

            # CSI-2 RX
            {
                'entity': CSI2_NAME,
                'routing': [
                    { 'src': (0, port), 'dst': (1 + ch_index, 0) },
                ],
                'pads': [
                    { 'pad': (0, port), 'fmt': mbus_fmt_tpg },
                    { 'pad': (1 + ch_index, 0), 'fmt': mbus_fmt_tpg },
                ],
            },
        ],

        'devices': [
            {
                'entity': f'rp1-cfe-csi2-ch{port}',
                'fmt': fmt_tpg,
            },
        ],

        'links': [
            { 'src': (ser_ent, 1), 'dst': (des_ent, port) },
            { 'src': (des_ent, des_src_pad), 'dst': (CSI2_NAME, 0) },
            { 'src': (CSI2_NAME, 1 + ch_index), 'dst': (f'rp1-cfe-csi2-ch{ch_index}', 0) },
        ],
    }

# Find serializers and sensors connected to the deserializer
def find_devices(mdev_name, deser_regex):
    md = v4l2.MediaDevice(*mdev_name)
    assert md
    deser = md.find_entity(regex=deser_regex)
    assert deser

    deser_src_pad = None
    for p in deser.pads:
        if p.is_source and len(p.links) == 1 and \
            p.links[0].sink.entity.name == CSI2_NAME:
            deser_src_pad = p.index
            break
    assert deser_src_pad is not None

    cameras = {}

    for p in deser.pads:
        if not p.is_sink:
            continue

        if len(p.links) == 0:
            continue

        assert len(p.links) == 1

        ser = p.links[0].source.entity
        sensor = ser.pads[0].links[0].source.entity

        cameras[p.index] = (ser.name, sensor.name)

    return deser.name, deser_src_pad, cameras

def get_configs(config_names):
    des_name, des_src_pad, cameras = find_devices(MEDIA_DEVICE_NAME, DESER_REGEX)

    cfgs = []
    ch_index = 0
    for i in cameras:
        cam = f'cam{i}'
        cam_meta = f'cam{i}-meta'
        ser_tpg = f'ser{i}-tpg'

        if cam in config_names:
            config_names.remove(cam)
            cfg = gen_ov5640_pixel(des_name, des_src_pad, ch_index, cameras, i)
            cfgs.append(cfg)
            ch_index += 1

        if ser_tpg in config_names:
            cfg = gen_ser_tpg(des_name, des_src_pad, ch_index, cameras, i)
            config_names.remove(ser_tpg)
            cfgs.append(cfg)
            ch_index += 1

    if 'des-tpg' in config_names:
        config_names.remove('des-tpg')
        cfg = gen_des_tpg(des_name, des_src_pad, ch_index)
        cfgs.append(cfg)
        ch_index += 1

    for config_name in config_names:
        print('Cannot find config "{}"'.format(config_name))

    if config_names:
        sys.exit(-1)

    merged_config = merge_configs(cfgs)

    return merged_config

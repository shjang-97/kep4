# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: service.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rservice.proto\x12\ttexttowav\"\x1f\n\x0bWavResponse\x12\x10\n\x08wav_file\x18\x01 \x01(\x0c\"g\n\x0bTextRequest\x12\x0c\n\x04text\x18\x01 \x01(\t\x12\x0b\n\x03sid\x18\x02 \x01(\x05\x12\x12\n\nctrl_pitch\x18\x03 \x01(\x05\x12\x12\n\nctrl_speed\x18\x04 \x01(\x02\x12\x15\n\rctrl_loudness\x18\x05 \x01(\x02\x32V\n\x10TextToWavService\x12\x42\n\x10\x43onvertTextToWav\x12\x16.texttowav.TextRequest\x1a\x16.texttowav.WavResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_WAVRESPONSE']._serialized_start=28
  _globals['_WAVRESPONSE']._serialized_end=59
  _globals['_TEXTREQUEST']._serialized_start=61
  _globals['_TEXTREQUEST']._serialized_end=164
  _globals['_TEXTTOWAVSERVICE']._serialized_start=166
  _globals['_TEXTTOWAVSERVICE']._serialized_end=252
# @@protoc_insertion_point(module_scope)

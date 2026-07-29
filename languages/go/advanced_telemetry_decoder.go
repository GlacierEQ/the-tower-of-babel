package main
import "encoding/binary"
type Frame struct { Seq uint32 }
func Decode(buf []byte) Frame { return Frame{Seq: binary.BigEndian.Uint32(buf[0:4])} }

import sys
sys.path.append("/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages")
import pcbnew


class Board:
    def __init__(self, width_mm, height_mm):
        self.board = pcbnew.BOARD()
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.create_rectangular_board_outline()

    def point(self, x_mm, y_mm):
        x = int(pcbnew.FromMM(x_mm))
        y = int(pcbnew.FromMM(y_mm))
        return pcbnew.VECTOR2I(x, y)

    def Add(self, *args, **kw):
        self.board.Add(*args, **kw)

    def add_shape(self, layer, shape_type):
        shape = pcbnew.PCB_SHAPE(self.board)
        shape.SetLayer(layer)
        shape.SetShape(shape_type)
        return shape

    def create_rectangular_board_outline(self):
        points = [
            self.point(0, 0),
            self.point(self.width_mm, 0),
            self.point(self.width_mm, self.height_mm),
            self.point(0, self.height_mm),
            self.point(0, 0),
        ]

        outline = self.add_shape(pcbnew.Edge_Cuts, pcbnew.SHAPE_T_POLY)
        outline.SetWidth(0)
        outline.SetPolyPoints(points)
        self.Add(outline)
        
    def add_wirebond_pad(
        self,
        width_mm,
        height_mm,
        center_x_mm,
        center_y_mm,
    ):
        top_left = (center_x_mm - width_mm / 2, center_y_mm - height_mm / 2)
        bottom_right = (center_x_mm + width_mm / 2, center_y_mm + height_mm / 2)

        pad = self.add_shape(pcbnew.F_Cu, pcbnew.SHAPE_T_RECT)
        pad.SetWidth(0)
        pad.SetStart(self.point(*top_left))  # top left corner
        pad.SetEnd(self.point(*bottom_right))  # bottom right corner
        pad.SetFilled(True)
        self.Add(pad)

        # add soldermask so that the pad is open
        mask = self.add_shape(pcbnew.F_Mask, pcbnew.SHAPE_T_RECT)
        mask.SetWidth(0)
        mask.SetStart(self.point(*top_left))  # top left corner
        mask.SetEnd(self.point(*bottom_right))  # bottom right corner
        mask.SetFilled(True)
        self.Add(mask)

    def add_plated_thru_hole(self, hole_diam_mm, position_xy_mm, pad_diam_mm=None):
        # Create a footprint to hold the pad
        footprint = pcbnew.FOOTPRINT(self.board)
        
        # Create the pad
        pad = pcbnew.PAD(footprint)
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(pad_diam_mm or hole_diam_mm * 2), 
                                    pcbnew.FromMM(pad_diam_mm or hole_diam_mm * 2)))
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        pad.SetLayerSet(pad.PTHMask())  # Makes it go through all layers
        pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(hole_diam_mm), 
                                        pcbnew.FromMM(hole_diam_mm)))
        pad.SetPosition(pcbnew.VECTOR2I(0, 0))  # Relative to footprint
        
        # Add pad to footprint
        footprint.Add(pad)
        
        # Now set the footprint position
        footprint.SetPosition(self.point(*position_xy_mm))
        
        # Add footprint to board
        self.board.Add(footprint)

    def add_trace(self, start_xy_mm, end_xy_mm, width_mm=0.25, layer=pcbnew.F_Cu):
        track = pcbnew.PCB_TRACK(self.board)
        track.SetStart(self.point(*start_xy_mm))
        track.SetEnd(self.point(*end_xy_mm))
        track.SetWidth(pcbnew.FromMM(width_mm))
        track.SetLayer(layer)
        self.board.Add(track)

    def add_chip_outline_to_top_silkscreen(self, chip_size_x_m, chip_size_y_mm):
        top_left = (self.width_mm / 2 - chip_size_x_m / 2, self.height_mm / 2 - chip_size_y_mm / 2)
        bottom_right = (self.width_mm / 2 + chip_size_x_m / 2, self.height_mm / 2 + chip_size_y_mm / 2)

        outline = self.add_shape(pcbnew.F_SilkS, pcbnew.SHAPE_T_RECT)
        outline.SetWidth(pcbnew.FromMM(0.25))
        outline.SetStart(self.point(*top_left))  # top left corner
        outline.SetEnd(self.point(*bottom_right))  # bottom right corner
        outline.SetFilled(False)
        self.Add(outline)

    def add_silkscreen_box(self, x1_mm, y1_mm, x2_mm, y2_mm, layer=pcbnew.F_SilkS, line_width_mm=0.15):
        """Add a rectangular box to silkscreen"""
        rect = pcbnew.PCB_SHAPE(self.board)
        rect.SetLayer(layer)
        rect.SetShape(pcbnew.SHAPE_T_RECT)
        rect.SetWidth(pcbnew.FromMM(line_width_mm))
        rect.SetStart(self.point(x1_mm, y1_mm))
        rect.SetEnd(self.point(x2_mm, y2_mm))
        rect.SetFilled(False)
        self.board.Add(rect)

    def add_text_to_top_silkscreen(
        self,
        text: str,
        x_mm: float,
        y_mm: float,
        size_mm: float = 1.0,
        rotation_degrees = 0,
        vertical_justify = "bottom",
    ):
        text_pcb = pcbnew.PCB_TEXT(self.board)
        text_pcb.SetLayer(pcbnew.F_SilkS)
        text_pcb.SetText(text)
        text_pcb.SetPosition(self.point(x_mm, y_mm))
        text_pcb.SetTextSize(pcbnew.VECTOR2I(int(size_mm * 1e6), int(size_mm * 1e6)))
        text_pcb.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)

        if vertical_justify == "bottom":
            text_pcb.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_BOTTOM)
        elif vertical_justify == "top":
            text_pcb.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_TOP)

        # Set rotation (KiCad uses tenths of degrees)
        text_pcb.SetTextAngle(pcbnew.EDA_ANGLE(rotation_degrees * 10, pcbnew.TENTHS_OF_A_DEGREE_T))

        self.board.Add(text_pcb)

    def add_serial_number_location_to_bottom_silkscreen(self):
        rect = self.add_shape(pcbnew.B_SilkS, pcbnew.SHAPE_T_RECT)
        width_mm = 10  # these are the dimensions of the rectangle required by JLCPCB
        height_mm = 2

        top_left = (self.width_mm / 2 - width_mm / 2, self.height_mm / 2 - height_mm / 2)
        bottom_right = (self.width_mm / 2 + width_mm / 2, self.height_mm / 2 + height_mm / 2)

        rect.SetWidth(0)
        rect.SetStart(self.point(*top_left))  # top left corner
        rect.SetEnd(self.point(*bottom_right))  # bottom right corner
        rect.SetFilled(True)
        self.Add(rect)

    def generate_gerbers(self, output_dir):
        pctl = pcbnew.PLOT_CONTROLLER(self.board)
        popt = pctl.GetPlotOptions()
        popt.SetOutputDirectory(output_dir)
        plot_format = pcbnew.PLOT_FORMAT_GERBER
        
        # Plot front copper layer
        pctl.SetLayer(pcbnew.F_Cu)
        pctl.OpenPlotfile("F_Cu", plot_format, "Top copper")
        pctl.PlotLayer()
        
        # Plot back copper layer
        pctl.SetLayer(pcbnew.B_Cu)
        pctl.OpenPlotfile("B_Cu", plot_format, "Bottom copper")
        pctl.PlotLayer()

        # Plot board outline layer
        pctl.SetLayer(pcbnew.Edge_Cuts)
        pctl.OpenPlotfile("Edge_Cuts", plot_format, "Board outline")
        pctl.PlotLayer()

        # Plot top solder mask layer
        pctl.SetLayer(pcbnew.F_Mask)
        pctl.OpenPlotfile("F_Mask", plot_format, "Top solder mask")
        pctl.PlotLayer()

        # Plot bottom solder mask layer
        pctl.SetLayer(pcbnew.B_Mask)
        pctl.OpenPlotfile("B_Mask", plot_format, "Bottom solder mask")
        pctl.PlotLayer()

        # Plot bottom silkscreen
        pctl.SetLayer(pcbnew.B_SilkS)
        pctl.OpenPlotfile("B_SilkS", plot_format, "Bottom silkscreen")
        pctl.PlotLayer()

        # Plot top silkscreen
        pctl.SetLayer(pcbnew.F_SilkS)
        pctl.OpenPlotfile("F_SilkS", plot_format, "Top silkscreen")
        pctl.PlotLayer()
        
        pctl.ClosePlot()

        # Generate drill files
        drill_writer = pcbnew.EXCELLON_WRITER(self.board)
        drill_writer.SetFormat(True)  # False = 2:4 format
        drill_writer.SetOptions(aMirror=False, aMinimalHeader=True, aOffset=pcbnew.VECTOR2I(0, 0), aMerge_PTH_NPTH=False)
        drill_writer.SetMapFileFormat(pcbnew.PLOT_FORMAT_GERBER)

        drill_writer.CreateDrillandMapFilesSet(output_dir, True, False)

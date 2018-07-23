import mido
import csv
from glob import glob
from Args import args


def write_csv():
    midipaths = glob(args.midifolder + '/*.mid')
    with open(args.csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        headers = ['Track name', 'instrument', 'instrument family', 'messages', 'note count', 'pitches', 'scale',
                   '2 sequences', '3 sequences', 'path']
        writer.writerow(headers)
        print_progress = len(midipaths)//10
        print('Total files: %d' % len(midipaths))
        for counter, path in enumerate(midipaths):
            filename = path.split("\\")[1]
            try:
                mid = mido.MidiFile(path)
                for track in mid.tracks:
                    info = track_info(track)
                    info.append(filename)
                    writer.writerow(info)
                if counter % print_progress == 0:
                    print('%2d%%' % (10 * counter // print_progress))

            except (IndexError, OSError, EOFError, Exception) as e:

                print(e, '\t', filename)
            except Exception as e:
                print('New error\t', e, filename)
                quit()


def track_info(track):
    n_info = note_info(track)
    instrument_info = get_program(track)

    info = [track.name.replace(',', ';'), instrument_info[0], instrument_info[1], len(track), n_info[0],
            n_info[1], n_info[2], n_info[3], n_info[4]]
    return info


def note_info(track):
    notes_count = 0
    count_unique_pitch = set()
    count_unique_notes = set()
    msg_1 = None
    msg_2 = None
    # sequence counting doesn't work with chords, but errormargin is not critical
    triple_sequences = set()
    double_sequences = set()
    channels = set()
    for i in range(len(track)):
        msg_0 = track[i]
        if msg_0.type == 'note_on':

            channels.add(msg_0.channel)
            if len(channels) > 1:
                # TODO multiple channel support
                raise Exception

            notes_count += 1
            count_unique_pitch.add(msg_0.note)
            count_unique_notes.add(msg_0.note % 12)
            if not msg_1:  # initializing the previous messages would be faster but would need another loop ==> messy
                if not msg_2:
                    msg_2 = msg_0
                    continue
                msg_1 = msg_0
                double_sequences.add(concentate_sequence(msg_2, msg_1))
                continue

            double_sequences.add(concentate_sequence(msg_1, msg_0))
            triple_sequences.add(concentate_sequence(msg_2, msg_1, msg_0))
            msg_2 = msg_1
            msg_1 = msg_0

    return notes_count, len(count_unique_pitch), len(count_unique_notes), len(double_sequences), len(triple_sequences)


def concentate_sequence(msg_2, msg_1, msg_0=None):
    if msg_0:
        return 10000 * msg_2.note + 100 * msg_1.note + msg_0.note
    else:
        return 100 * msg_2.note + msg_1.note


def get_program(track):
    #  program list from https://www.midi.org/specifications-old/item/gm-level-1-sound-set
    program = 'Acoustic Grand Piano'
    instrument_family = 'Piano'
    for msg in track:
        if msg.type == 'program_change':
            program_number = msg.program
            program = args.instruments[program_number]
            instrument_family = args.instrument_family[program_number]
            break

    return program, instrument_family


if __name__ == "__main__":
    write_csv()

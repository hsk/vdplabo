// sprite/test/input/README.md で定義する共通JSON形式(フレーム番号ベースの
// キー入力スクリプト)をC++(SDL2)版エンジンから読み込むためのヘッダオンラ
// イン実装。
//
// このスキーマ専用の最小限のJSONパーサ(汎用JSONライブラリは未導入のため)。
// 対応するのは {"fps": number, "events": [{"frame": int, "key": string,
// "action": "down"|"up"}, ...]} という固定形のみ。
//
// キー名はsprite/test/input/input_script.pyのKEY_MATRIXと同じ論理キー名だが、
// ここではまだ実際にキー入力を消費するエンジンが無いため、よく使うキー
// (矢印・SPACE・文字・数字・ENTER・ESC・修飾キー・F1-F5)だけをSDL_Scancode
// に対応させてある。不足分はKEY_TABLEに追記すること。
#pragma once

#include <SDL.h>

#include <algorithm>
#include <cctype>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace input_script {

struct Event {
    int frame;
    SDL_Scancode scancode;
    bool pressed;  // true = down, false = up
};

// 論理キー名 -> SDL_Scancode。GRAPH/CODEはMSXに専用キーが無いホスト向けの
// 慣例的な割り当て(GRAPH=左Alt, CODE=右Alt)であり、openMSX側の仕様ではない。
inline const std::unordered_map<std::string, SDL_Scancode>& key_table() {
    static const std::unordered_map<std::string, SDL_Scancode> table = {
        {"0", SDL_SCANCODE_0}, {"1", SDL_SCANCODE_1}, {"2", SDL_SCANCODE_2},
        {"3", SDL_SCANCODE_3}, {"4", SDL_SCANCODE_4}, {"5", SDL_SCANCODE_5},
        {"6", SDL_SCANCODE_6}, {"7", SDL_SCANCODE_7}, {"8", SDL_SCANCODE_8},
        {"9", SDL_SCANCODE_9},
        {"A", SDL_SCANCODE_A}, {"B", SDL_SCANCODE_B}, {"C", SDL_SCANCODE_C},
        {"D", SDL_SCANCODE_D}, {"E", SDL_SCANCODE_E}, {"F", SDL_SCANCODE_F},
        {"G", SDL_SCANCODE_G}, {"H", SDL_SCANCODE_H}, {"I", SDL_SCANCODE_I},
        {"J", SDL_SCANCODE_J}, {"K", SDL_SCANCODE_K}, {"L", SDL_SCANCODE_L},
        {"M", SDL_SCANCODE_M}, {"N", SDL_SCANCODE_N}, {"O", SDL_SCANCODE_O},
        {"P", SDL_SCANCODE_P}, {"Q", SDL_SCANCODE_Q}, {"R", SDL_SCANCODE_R},
        {"S", SDL_SCANCODE_S}, {"T", SDL_SCANCODE_T}, {"U", SDL_SCANCODE_U},
        {"V", SDL_SCANCODE_V}, {"W", SDL_SCANCODE_W}, {"X", SDL_SCANCODE_X},
        {"Y", SDL_SCANCODE_Y}, {"Z", SDL_SCANCODE_Z},
        {"SPACE", SDL_SCANCODE_SPACE}, {"RETURN", SDL_SCANCODE_RETURN},
        {"ESC", SDL_SCANCODE_ESCAPE}, {"TAB", SDL_SCANCODE_TAB},
        {"BS", SDL_SCANCODE_BACKSPACE}, {"STOP", SDL_SCANCODE_PAUSE},
        {"SELECT", SDL_SCANCODE_INSERT}, {"HOME", SDL_SCANCODE_HOME},
        {"INS", SDL_SCANCODE_INSERT}, {"DEL", SDL_SCANCODE_DELETE},
        {"LEFT", SDL_SCANCODE_LEFT}, {"RIGHT", SDL_SCANCODE_RIGHT},
        {"UP", SDL_SCANCODE_UP}, {"DOWN", SDL_SCANCODE_DOWN},
        {"SHIFT", SDL_SCANCODE_LSHIFT}, {"CTRL", SDL_SCANCODE_LCTRL},
        {"GRAPH", SDL_SCANCODE_LALT}, {"CODE", SDL_SCANCODE_RALT},
        {"CAPS", SDL_SCANCODE_CAPSLOCK},
        {"F1", SDL_SCANCODE_F1}, {"F2", SDL_SCANCODE_F2}, {"F3", SDL_SCANCODE_F3},
        {"F4", SDL_SCANCODE_F4}, {"F5", SDL_SCANCODE_F5},
    };
    return table;
}

namespace detail {

// {"fps": .., "events": [...]} のみを想定した最小限のJSON値パーサ。
class JsonParser {
public:
    explicit JsonParser(const std::string& text) : text_(text) {}

    struct Value {
        enum class Type { Object, Array, String, Number, Other } type = Type::Other;
        std::unordered_map<std::string, Value> object;
        std::vector<Value> array;
        std::string string_value;
        double number_value = 0;
    };

    Value parse() {
        skip_ws();
        Value v = parse_value();
        return v;
    }

private:
    const std::string& text_;
    size_t pos_ = 0;

    void skip_ws() {
        while (pos_ < text_.size() && std::isspace(static_cast<unsigned char>(text_[pos_]))) pos_++;
    }

    char peek() {
        if (pos_ >= text_.size()) throw std::runtime_error("input_script: unexpected end of JSON");
        return text_[pos_];
    }

    Value parse_value() {
        skip_ws();
        char c = peek();
        if (c == '{') return parse_object();
        if (c == '[') return parse_array();
        if (c == '"') return parse_string();
        return parse_number();
    }

    Value parse_object() {
        Value v;
        v.type = Value::Type::Object;
        pos_++;  // '{'
        skip_ws();
        if (peek() == '}') { pos_++; return v; }
        while (true) {
            skip_ws();
            Value key = parse_string();
            skip_ws();
            if (peek() != ':') throw std::runtime_error("input_script: expected ':'");
            pos_++;
            Value val = parse_value();
            v.object[key.string_value] = val;
            skip_ws();
            char c = peek();
            if (c == ',') { pos_++; continue; }
            if (c == '}') { pos_++; break; }
            throw std::runtime_error("input_script: expected ',' or '}'");
        }
        return v;
    }

    Value parse_array() {
        Value v;
        v.type = Value::Type::Array;
        pos_++;  // '['
        skip_ws();
        if (peek() == ']') { pos_++; return v; }
        while (true) {
            v.array.push_back(parse_value());
            skip_ws();
            char c = peek();
            if (c == ',') { pos_++; continue; }
            if (c == ']') { pos_++; break; }
            throw std::runtime_error("input_script: expected ',' or ']'");
        }
        return v;
    }

    Value parse_string() {
        Value v;
        v.type = Value::Type::String;
        if (peek() != '"') throw std::runtime_error("input_script: expected string");
        pos_++;
        std::string out;
        while (peek() != '"') {
            char c = text_[pos_++];
            if (c == '\\' && pos_ < text_.size()) {
                out += text_[pos_++];
            } else {
                out += c;
            }
        }
        pos_++;  // closing '"'
        v.string_value = out;
        return v;
    }

    Value parse_number() {
        Value v;
        v.type = Value::Type::Number;
        size_t start = pos_;
        while (pos_ < text_.size() &&
               (std::isdigit(static_cast<unsigned char>(text_[pos_])) ||
                text_[pos_] == '-' || text_[pos_] == '+' || text_[pos_] == '.' ||
                text_[pos_] == 'e' || text_[pos_] == 'E')) {
            pos_++;
        }
        if (pos_ == start) throw std::runtime_error("input_script: expected number");
        v.number_value = std::stod(text_.substr(start, pos_ - start));
        return v;
    }
};

}  // namespace detail

// 読み込んだinput scriptをフレーム番号順に保持し、メインループから
// 毎フレーム events_due(frame) を呼ぶことで消費する。
class InputScript {
public:
    static InputScript load(const std::string& path) {
        std::ifstream f(path);
        if (!f) throw std::runtime_error("input_script: cannot open " + path);
        std::stringstream ss;
        ss << f.rdbuf();
        std::string text = ss.str();

        detail::JsonParser parser(text);
        auto root = parser.parse();

        InputScript script;
        auto fps_it = root.object.find("fps");
        script.fps_ = (fps_it != root.object.end()) ? static_cast<int>(fps_it->second.number_value) : 60;

        auto events_it = root.object.find("events");
        if (events_it != root.object.end()) {
            for (const auto& raw : events_it->second.array) {
                int frame = static_cast<int>(raw.object.at("frame").number_value);
                const std::string& key = raw.object.at("key").string_value;
                const std::string& action = raw.object.at("action").string_value;
                auto it = key_table().find(key);
                if (it == key_table().end()) {
                    throw std::runtime_error("input_script: unknown key '" + key +
                                              "' (add it to key_table() in input_script.hpp)");
                }
                script.events_.push_back(Event{frame, it->second, action == "down"});
            }
        }
        std::stable_sort(script.events_.begin(), script.events_.end(),
                          [](const Event& a, const Event& b) { return a.frame < b.frame; });
        return script;
    }

    int fps() const { return fps_; }

    // frame引数は呼ぶたびに単調増加させること(メインループのフレーム
    // カウンタをそのまま渡す想定)。前回呼び出し以降にframe以下になった
    // イベントをすべてまとめて返す(フレーム飛びにも対応するため)。
    std::vector<Event> events_due(int frame) {
        std::vector<Event> due;
        while (cursor_ < events_.size() && events_[cursor_].frame <= frame) {
            due.push_back(events_[cursor_]);
            cursor_++;
        }
        return due;
    }

private:
    int fps_ = 60;
    std::vector<Event> events_;
    size_t cursor_ = 0;
};

}  // namespace input_script

wp=$(realpath $1)

hyprctl hyprpaper preload $wp
hyprctl hyprpaper wallpaper , $wp
wallust run $wp
killall waybar
waybar &
notify-send -t 2000 -i $wp "Theme updated" "The theme has been successfully updated to $wp."
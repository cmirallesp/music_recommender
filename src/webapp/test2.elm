import Json.Decode exposing (field, int, string, Decoder)
import Html exposing (text, div, input, button, p, select,label, Html)
import Html.Attributes exposing (value,multiple)
import Html.Events exposing (onClick, onInput)
import Html exposing (program)
import Http exposing (get, Error, Response, Error(..))
import Task  exposing (Task, succeed, fail, andThen, mapError)   


main =
  Html.program
    { init = init 
    , view = view
    , update = update
    , subscriptions = subscriptions
    }

subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none



-- MODEL

type alias Artist =
  { id : String
  , full_name : String
  }

type alias Model =
  { artists : List Artist
  , added: List Artist
  }

init : (Model, Cmd Msg)
init =
  ( Model [] [], Cmd.none )

decoder : Decoder (List Artist)
decoder =
    Json.Decode.list artistDecoder

artistDecoder : Decoder Artist
artistDecoder =
    Json.Decode.map2 Artist
        (field "id"  string)
        (field "full_name" string)



-- update

type Msg
  = GetAllArtists
  | AddArtist (Artist)
  | LoadArtists (Result Http.Error (List Artist))


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    AddArtist artist->
      if (List.member artist model.added) then
        (model, Cmd.none)
      else
        ({model | added=artist::model.added} , Cmd.none)  
        

    GetAllArtists ->
      (model, getAllArtists "")

    LoadArtists (Ok lstArtists) ->
      ( { model | artists=lstArtists }, Cmd.none)

    LoadArtists (Err _) ->
      (model, Cmd.none)


getAllArtists : String -> Cmd Msg
getAllArtists _=
  sendGet LoadArtists ("http://localhost:8887/artists") decoder

sendGet : (Result Error a -> msg) -> String -> Decoder a -> Cmd msg
sendGet msg url decoder =
  Http.get url decoder |> Http.send msg
    


-- VIEW

view : Model -> Html Msg
view model =
        div []
        [ button [ onClick GetAllArtists ] [ text "Search" ]
        , div
            []
            (List.map (\artist -> 
              div []
                [ label [] [ text artist.full_name ]
                , button [onClick (AddArtist artist)] [text "Add"]
                ]
            ) model.artists)
        , div
          []
          (List.map (\artists ->
            div []
              [ label [] [text artists.full_name]]) model.added)
        ]
        